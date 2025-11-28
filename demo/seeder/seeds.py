import logging
import os
import uuid
import requests
import yaml


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:9000")
DATA_PATH = "data.yaml"

logger = logging.getLogger(__name__)

def send_request(method, endpoint, body=None):
    url = f'{API_BASE_URL}{endpoint}'

    logger.debug(f'Sending {method} request to {url} with body: {body}')
    response = requests.request(
        method=method, 
        headers={"Content-Type": "application/json"},
        url=url, 
        json=body
    )

    if response.status_code != 200:
        logger.error(f'Request to {url} failed with status code {response.status_code}: {response.text}')

    return response

def create_project(project_name, project_description):
    project_data = {
        "@type":"Project",
        "name": project_name,
        "description": project_description 
    }

    response = send_request("POST", "/projects", project_data)

    if response.status_code == 200:
        project = response.json()
        return project
    else:
        print("Problem in creating the project")

def push_commit(project_id, branch_id, change):
    commit_post_url = f"/projects/{project_id}/commits?branchId={branch_id}"
    commit_body = {
        "@type": "Commit",
        "change": change
    }
    logger.debug(f"Creating commit {commit_body}")
    response = send_request("POST", commit_post_url, commit_body)
    
    if response.status_code == 200:
        commit_response_json = response.json()
        return commit_response_json.get('@id')
    else:
        print(f"Problem in creating commit {change} for project {project_id}")
        print(response)
        return None
    
def build_change_list(elements, owner_id=None, id_map=None):
    """
    Build a flat list of DataVersion change objects from a hierarchical
    YAML element list. Also optionally fills id_map[name] = @id.
    """
    if id_map is None:
        id_map = {}

    change = []

    for element in elements:
        element_id = str(uuid.uuid4())

        # remember the id if you want to look it up later by name
        id_map[element["name"]] = element_id

        payload = {
            "name": element["name"],
            "@type": element["type"],
        }

        # Only set owner if we actually have a parent owner_id
        if owner_id is not None:
            payload["owner"] = {"@id": owner_id}

        data_version = {
            "@type": "DataVersion",
            "identity": {
                "@id": element_id,
                # some examples use "@type": "string" here; often not required,
                # but you can add it if your API expects it:
                # "@type": "string"
            },
            "payload": payload
        }
        change.append(data_version)

        # Recursively add children, passing this element's id as owner
        children = element.get("children", [])
        if children:
            change.extend(
                build_change_list(children, owner_id=element_id, id_map=id_map)
            )

    return change

def parse_project(data):
    response = create_project(data["name"], "")
    if not response:
        return

    project_id = response["@id"]
    branch_main_id = response["defaultBranch"]["@id"]

    for branch in data["branches"]:
        if branch["name"] == "main":
            # Build hierarchical elements -> flat DataVersion list
            id_map = {}
            change = build_change_list(branch["elements"], owner_id=None, id_map=id_map)

            # Now you know every @id, without asking the server:
            # e.g. id_map["WaterHeater"] gives you the UUID you assigned.

            push_commit(project_id, branch_main_id, change)


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Iterate Projects
    for proj in data.get("projects", []):
        parse_project(proj)

if __name__ == "__main__":
    main()
