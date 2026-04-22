from flask import Flask, request, jsonify
from flask_cors import CORS

from src.change import engine
from src.context.context_manager import ContextManager
from src.sysml2.sysml_client import SysMLClient
from src.utils.logger import initialize_logger


app = Flask(__name__)
CORS(app)


@app.route(
    "/projects/<string:projectId>/branches/<string:branchId>/change", methods=["POST"]
)
def change_endpoint(projectId, branchId):
    data = request.get_json()

    if not data or "change_request" not in data:
        return jsonify({"error": "Invalid request. Missing change_request."}), 400
    change_request = data["change_request"]

    res, code = engine.run(projectId, branchId, change_request)

    return jsonify(res), code


@app.route(
    "/projects/<string:projectId>/branches/<string:branchId>/context", methods=["POST"]
)
def context_endpoint(projectId, branchId):
    data = request.get_json()

    if not data or "context_request" not in data:
        return jsonify({"error": "Invalid request. Missing context_request."}), 400
    context_request = data["context_request"]

    try:
        client = SysMLClient()
        client.initialize(projectId, branchId)

        context_manager = ContextManager(client)
        context = context_manager.create_context(context_request)

        return jsonify({"status": "success", "context": context}), 200
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


if __name__ == "__main__":
    initialize_logger()
    app.run(debug=True)
