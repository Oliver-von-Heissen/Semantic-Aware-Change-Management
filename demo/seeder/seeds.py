import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:9000")
DATA_PATH = "data.json"

# Endpoints
ENDPOINTS = {
    "PROJECTS": "/projects",
    "COMMITS": "/projects/{project_id}/commits",
}

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Use a Session for connection pooling
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))


def send_request(method: str, endpoint: str, body: Any = None) -> requests.Response:
    url = f"{API_BASE_URL}{endpoint}"
    logger.debug(f"Sending {method} request to {url} with body: {body}")

    try:
        response = session.request(
            method=method,
            headers={"Content-Type": "application/json"},
            url=url,
            json=body,
            timeout=10,
        )
        # Raise exception for 4xx or 5xx status codes
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response body: {e.response.text}")
        raise


def create_project(project_name: str, project_description: str) -> Dict[str, Any]:
    project_data = {
        "@type": "Project",
        "name": project_name,
        "description": project_description,
    }

    response = send_request("POST", ENDPOINTS["PROJECTS"], project_data)
    return response.json()


def push_commit(
    project_id: str, branch_id: str, change: List[Dict[str, Any]]
) -> Optional[str]:
    endpoint = (
        ENDPOINTS["COMMITS"].format(project_id=project_id) + f"?branchId={branch_id}"
    )
    commit_body = {"@type": "Commit", "change": change}

    logger.info(f"Pushing commit with {len(change)} changes to project {project_id}")
    response = send_request("POST", endpoint, commit_body)

    return response.json().get("@id")


def build_change_list(
    parts: List[Dict], connections: List[Dict], id_map: Dict[str, str]
) -> List[Dict]:
    """
    Build a flat list of DataVersion change objects from a system's flat
    `parts` list and `connections` list. A composition connection
    (from -> to) makes the `to` part owned by the `from` part.
    Also fills id_map[json_id] = @id for later lookup.
    """
    # Derive ownership from composition connections: child -> parent
    parent_of = {
        conn["toBlockId"]: conn["fromBlockId"]
        for conn in connections
        if conn.get("type") == "composition"
    }
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


def parse_system(system: Dict[str, Any]):
    try:
        project = create_project(system["name"], "")
        project_id = project["@id"]
        branch_main_id = project["defaultBranch"]["@id"]

        id_map = {}
        change = build_change_list(
            system.get("parts", []),
            system.get("connections", []),
            id_map=id_map,
        )

        push_commit(project_id, branch_main_id, change)
        logger.info(f"Successfully seeded system: {system['name']}")
    except Exception as e:
        logger.error(f"Failed to parse system {system.get('name', 'Unknown')}: {e}")


def main():
    if not os.path.exists(DATA_PATH):
        logger.error(f"Data file not found: {DATA_PATH}")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f) or {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            return

    systems = data.get("systems", [])
    logger.info(f"Found {len(systems)} systems to seed.")

    for system in systems:
        parse_system(system)


if __name__ == "__main__":
    main()
