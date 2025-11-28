import datetime
import logging
import time
from src.context.context_manager import ContextManager
from src.external.llm_service import create_llm_prompt, send_llm_request
from src.sysml2.sysml_client import SysMLClient
from src.sysml2.tooling import execute_tool, make_tools
from src.utils.json_sanitize import sanitize
logger = logging.getLogger(__name__)


def run(project_id, branch_id, change_request):
    start_time = time.time()
    logger.info(f"Starting engine on project {project_id}, branch {branch_id}")
    runner_logs = []

    try:
        # Initialize Project Handler
        client = SysMLClient()
        client.initialize(project_id, branch_id)

        # Prepare context
        context_manager = ContextManager(client)
        context = context_manager.create_context(change_request)

        # Fetch full context for comparison with naive approach
        context_naive = client.get_all_elements()
        sanitized_naive_elements = sanitize(context_naive) # sanitize naive baseline for better comparison
        _, input_naive = create_llm_prompt(str(sanitized_naive_elements), change_request)

        # create tools
        tools = make_tools(client)
        tools_by_name = {t.name: t for t in tools}

        # process change
        response, input_token, output_token = send_llm_request(context=str(context), user_request=change_request, tools=tools)

        for tool_call in response:
            msg = execute_tool(tools_by_name, tool_call)
            runner_logs.append({
                "message": msg,
            })

        # Push Changes
        client.commit_and_push()

        # Calculate processing time
        processing_time = time.time() - start_time

        result = {
            "status": "success",
            "metadata": {
                "project_id": project_id,
                "branch_id": branch_id,
                "change_request": change_request,
                "timestamp": datetime.datetime.now().isoformat()
            },
            "processing_time_seconds": round(processing_time, 3),
            "tokens": {
                "input_approach": input_token,
                "input_naive": input_naive,
                "output": output_token,
            },
            "logs": runner_logs,
        }

        return result, 200
    
    except Exception as e:
        processing_time = time.time() - start_time
        error_result = {
            "status": "error",
            "metadata": {
                "project_id": project_id,
                "branch_id": branch_id,
                "change_request": change_request,
                "timestamp": datetime.datetime.now().isoformat()
            },
            "processing_time_seconds": round(processing_time, 3),
            "error": str(e),
            "logs": runner_logs,
        }
        logger.error(f"Error processing request: {e}")
        return error_result, 500
    