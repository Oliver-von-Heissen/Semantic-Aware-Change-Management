import logging
from src.external.rest_service import send_request
logger = logging.getLogger(__name__)

def push_commit(project_id, change):
    commit_post_url = f"/projects/{project_id}/commits"
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
