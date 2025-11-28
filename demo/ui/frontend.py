import os
from typing import Dict, List, Optional, Set
import requests
import streamlit as st

st.set_page_config(page_title="Semantic-Aware Change management", layout="centered")

# ----------------------------
# Configuration
# ----------------------------

SYSML_API_URL = os.environ.get("SYSML_API_URL", "http://localhost:9000")
CHANGE_ENGINE_URL = os.environ.get("CHANGE_ENGINE_URL", "http://localhost:8000")

# ----------------------------
# REST helpers
# ----------------------------

def _safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET failed: {e}")
        return None

def _safe_post(url, json_body=None):
    try:
        r = requests.post(url, json=json_body, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"POST failed: {e}")
        return None

# ----------------------------
# API wrapper functions
# ----------------------------

@st.cache_data(show_spinner=True)
def get_projects():
    return _safe_get(f"{SYSML_API_URL}/projects") or []

@st.cache_data(show_spinner=True)
def get_branches(project_id: str):
    return _safe_get(f"{SYSML_API_URL}/projects/{project_id}/branches") or []

def get_branches_for_commit(project_id: str):
    return _safe_get(f"{SYSML_API_URL}/projects/{project_id}/branches") or []

def get_commits(project_id, branch_id):
    return _safe_get(f"{SYSML_API_URL}/projects/{project_id}/branches") or []

def get_model(project_id: str, commit_id: str):
    return _safe_get(f"{SYSML_API_URL}/projects/{project_id}/commits/{commit_id}/elements") or {}

def send_change_request(project_id: str, branch_id: str, description: str):
    payload = {"change_request": description}
    return _safe_post(f"{CHANGE_ENGINE_URL}/projects/{project_id}/branches/{branch_id}/change", json_body=payload) or {"status": "error"}

# ----------------------------
# UI helpers
# ----------------------------

def update_head_commit(project_id, branch_id):
    branches = get_branches_for_commit(project_id)
    # Find the branch that matches the provided branch_id
    for branch in branches:
        if branch.get("@id") == branch_id:
            # Store the head commit SHA in session state
            st.session_state["head_commit"] = branch["head"]["@id"]
            break

def _normalize_id(value) -> Optional[str]:
    """Return the string '@id' from a value shaped like {'@id': ...} or a string."""
    if value is None:
        return None
    if isinstance(value, dict):
        return str(value.get("@id")) if value.get("@id") is not None else None
    return str(value)

def model_to_markdown(elements: List[dict]) -> str:
    """Convert elements to markdown; indent owned elements under their owner (@id)."""
    id_map: Dict[str, dict] = {}
    order: List[str] = []

    # Map elements by normalized @id, fallback to index if missing/duplicate
    for i, elem in enumerate(elements):
        eid = _normalize_id(elem.get("@id"))
        if not eid or eid in id_map:
            eid = f"__idx_{i}"
        id_map[eid] = elem
        order.append(eid)

    # Build ownership relationships
    children: Dict[str, List[str]] = {eid: [] for eid in id_map}
    roots: List[str] = []
    for eid in order:
        owner_id = _normalize_id(id_map[eid].get("owner"))
        if owner_id and owner_id in id_map and owner_id != eid:
            children[owner_id].append(eid)
        else:
            roots.append(eid)

    # DFS with cycle detection
    lines: List[str] = []
    visiting: Set[str] = set()

    def add_line(cur_id: str, depth: int) -> None:
        if cur_id in visiting:
            lines.append("  " * depth + f"- [cycle detected at {cur_id}]")
            return
        visiting.add(cur_id)

        elem = id_map[cur_id]
        name = (elem.get("name") or "").strip() or "(unnamed)"
        etype = (elem.get("@type") or "").strip()
        detail = f" ({etype})" if etype else ""
        lines.append("  " * depth + f"- {name}{detail}")

        for child_id in children.get(cur_id, []):
            add_line(child_id, depth + 1)

        visiting.remove(cur_id)

    for root_id in roots:
        add_line(root_id, 0)

    return "\n".join(lines)

def clear_cache():
    for key in ("model_cache", "model_branch"):
        if key in st.session_state:
            del st.session_state[key]

# ----------------------------
# UI
# ----------------------------

st.title("Semantic-Aware Change Management Demonstrator")
st.header("Model Management")

# Project selection

projects = get_projects()
project_options = ["Please choose..."] + [p["name"] for p in projects]
selected_project_name = st.selectbox("Project", project_options, index=0, key="project_select")

selected_project_id = None
if selected_project_name != "Please choose...":
    selected_project_id = next((p["@id"] for p in projects if p["name"] == selected_project_name), None)

# Branch selection (depends on project)

branches = []
if selected_project_id:
    branches = get_branches(selected_project_id)

branch_options = ["Please choose..."] + [b["name"] for b in branches]
selected_branch_name = st.selectbox("Branch", branch_options, index=0, key="branch_select")

selected_branch_id = None
if selected_branch_name != "Please choose...":
    selected_branch_id = next(((b["@id"]) for b in branches if b["name"] == selected_branch_name), None)

# Commit Update

if selected_branch_id:
    # Update head commit when branch changes
    if st.session_state.get("current_branch") != selected_branch_id:
        update_head_commit(selected_project_id, selected_branch_id)
        st.session_state["current_branch"] = selected_branch_id
        clear_cache()

# Model display

st.subheader("Model")

if selected_branch_id:
    if "model_cache" not in st.session_state or st.session_state.get("model_branch") != selected_branch_id:
        # First time or branch changed -> fetch fresh model
        model = get_model(selected_project_id, st.session_state["head_commit"])
        st.session_state["model_cache"] = model
        st.session_state["model_branch"] = selected_branch_id
    else:
        # Use the already‑fetched model
        model = st.session_state["model_cache"]

    if model:
        st.text(model_to_markdown(model))
    else:
        st.info("No model available.")
else:
    st.info("Please select a project and a branch to view a model.")

st.markdown("---")

# Change request

st.header("Change Management")

change_desc = st.text_input("Change Request", placeholder="Please desribe your desired change...", key="change_desc")
send_clicked = st.button("Apply change", use_container_width=True)

if send_clicked:
    if not selected_branch_id:
        st.warning("Please choose a branch first.")
    elif not change_desc.strip():
        st.warning("Please enter a change description.")
    else:
        with st.spinner("Sending change request..."):
            res = send_change_request(selected_project_id, selected_branch_id, change_desc.strip())

            if not res:
                st.stop()  # already showed error in _safe_post

            # Save return value to session so they persist across rerun
            st.session_state["processing_time_seconds"] = res.get("processing_time_seconds", [])
            tokens = res.get("tokens", {})
            if isinstance(tokens, dict):
                st.session_state["input_approach"] = tokens.get("input_approach", [])
                st.session_state["input_naive"] = tokens.get("input_naive", [])
                st.session_state["output"] = tokens.get("output", [])
            st.session_state["logs"] = res.get("logs", [])

            # Refresh model: update head commit, clear cache, then rerun
            update_head_commit(selected_project_id, selected_branch_id)
            clear_cache()

            # Force UI to re-execute so the "Model" section fetches the new commit
            try:
                st.rerun()  # Streamlit >= 1.27
            except Exception:
                st.experimental_rerun()  # fallback for older versions

if st.session_state.get("processing_time_seconds"):
    st.subheader("Processing time")
    st.markdown(str(st.session_state["processing_time_seconds"]) + " seconds")
if st.session_state.get("output"):
    st.subheader("Token Usage")
    naive = st.session_state["input_naive"]
    sacm = st.session_state["input_approach"]
    st.markdown("Input SACM: " + str(sacm) + " token")
    st.markdown("Input Naive: " + str(naive) + " token")
    reduction = ((naive - sacm) / naive) * 100
    st.markdown(f"Reduction: {reduction:.1f}% (SACM vs. Naive)")
    st.markdown("Output: " + str(st.session_state["output"]) + " token")
if st.session_state.get("logs"):
    st.subheader("Logs")
    st.markdown("\n".join(f"- {entry}" for entry in st.session_state["logs"]))
