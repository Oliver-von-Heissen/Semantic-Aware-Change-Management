from src.external.rest_service import send_request


def get_project_elements(project_id, commit_id):
    elements_get_url = f"/projects/{project_id}/commits/{commit_id}/elements"
    response = send_request("GET", elements_get_url)
    
    if response.status_code == 200:
        elements_response_json = response.json()
        return elements_response_json
    else:
        print(f"Problem in fetching elements for project {project_id} with commit {commit_id}")
        print(response)
        return None
    
def get_project_element(project_id, commit_id, element_id):
    element_get_url = f"/projects/{project_id}/commits/{commit_id}/elements/{element_id}"
    response = send_request("GET", element_get_url)
    
    if response.status_code == 200:
        elements_response_json = response.json()
        return elements_response_json
    else:
        print(f"Problem in fetching elements for project {project_id} with commit {commit_id}")
        print(response)
        return None