from src.external.rest_service import send_request


def get_datatypes():
    meta_datatype_get_url = "/meta/datatypes"
    response = send_request("GET", meta_datatype_get_url)

    if response.status_code == 200:
        commit_response_json = response.json()
        return commit_response_json
    else:
        print(f"Problem in fetching meta datatypes")
        print(response)
        return None