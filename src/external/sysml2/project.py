import pprint
from src.external.rest_service import send_request


def get_all_projects():
    response = send_request("GET", "/projects")

    if response.status_code == 200:
        projects = response.json()
        return projects
    else:
        pprint("Problem in fetching projects")

def get_project(project_id):
    project_get_url = f"/projects/{project_id}"
    response = send_request("GET", project_get_url)

    if response.status_code == 200:
        project = response.json()
        return project
    else:
        print("Problem in fetching project")

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