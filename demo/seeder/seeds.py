import json
import logging
import os
import uuid
import requests


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:9000")
DATA_PATH = "data.json"

logger = logging.getLogger(__name__)


def send_request(method, endpoint, body=None):
    url = f"{API_BASE_URL}{endpoint}"

    logger.debug(f"Sending {method} request to {url} with body: {body}")
    response = requests.request(
        method=method, headers={"Content-Type": "application/json"}, url=url, json=body
    )

    if response.status_code != 200:
        logger.error(
            f"Request to {url} failed with status code {response.status_code}: {response.text}"
        )

    return response


def create_project(project_name, project_description):
    project_data = {
        "@type": "Project",
        "name": project_name,
        "description": project_description,
    }

    response = send_request("POST", "/projects", project_data)

    if response.status_code == 200:
        project = response.json()
        return project
    else:
        print("Problem in creating the project")


def push_commit(project_id, branch_id, change):
    commit_post_url = f"/projects/{project_id}/commits?branchId={branch_id}"
    commit_body = {"@type": "Commit", "change": change}
    logger.debug(f"Creating commit {commit_body}")
    response = send_request("POST", commit_post_url, commit_body)

    if response.status_code == 200:
        commit_response_json = response.json()
        return commit_response_json.get("@id")
    else:
        print(f"Problem in creating commit {change} for project {project_id}")
        print(response)
        return None


def build_change_list(parts, connections, id_map=None):
    """
    Build a flat list of DataVersion change objects from a system's flat
    `parts` list and `connections` list. A composition connection
    (from -> to) makes the `to` part owned by the `from` part.
    Also fills id_map[json_id] = @id for later lookup.
    """
    if id_map is None:
        id_map = {}

    # Derive ownership from composition connections: child -> parent
    parent_of = {}
    for connection in connections:
        if connection.get("type") == "composition":
            parent_of[connection["toBlockId"]] = connection["fromBlockId"]

    # Assign a server @id to every part up front so owners can be referenced
    for part in parts:
        id_map[part["id"]] = str(uuid.uuid4())

    change = []
    for part in parts:
        element_id = id_map[part["id"]]

        payload = {
            "name": part["name"],
            "@type": "PartDefinition",
        }

        parent_json_id = parent_of.get(part["id"])
        if parent_json_id is not None:
            payload["owner"] = {"@id": id_map[parent_json_id]}

        change.append(
            {
                "@type": "DataVersion",
                "identity": {
                    "@id": element_id,
                },
                "payload": payload,
            }
        )

    return change


def parse_system(system):
    response = create_project(system["name"], "")
    if not response:
        return

    project_id = response["@id"]
    branch_main_id = response["defaultBranch"]["@id"]

    id_map = {}
    change = build_change_list(
        system.get("parts", []),
        system.get("connections", []),
        id_map=id_map,
    )

    # Now you know every @id, without asking the server:
    # e.g. id_map["b6"] gives you the UUID you assigned.

    push_commit(project_id, branch_main_id, change)


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f) or {}

    # Iterate Systems
    for system in data.get("systems", []):
        parse_system(system)


if __name__ == "__main__":
    main()
