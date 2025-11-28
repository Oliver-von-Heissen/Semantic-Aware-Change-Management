from src.external.rest_service import send_request


def get_project_branches(project_id):
    branches_get_url = f"/projects/{project_id}/branches"
    response = send_request("GET", branches_get_url)

    if response.status_code == 200:
        branches = response.json()
        return branches
    else:
        print("Problem in fetching branches")

def get_project_branch(project_id, branch_id):
    branch_get_url = f"/projects/{project_id}/branches/{branch_id}"
    response = send_request("GET", branch_get_url)

    if response.status_code == 200:
        branch = response.json()
        return branch
    else:
        print("Problem in fetching branches")
        