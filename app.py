from flask import Flask, request, jsonify
from flask_cors import CORS

from src.change import engine
from src.utils.logger import initialize_logger

app = Flask(__name__)
CORS(app)


@app.route('/projects/<string:projectId>/branches/<string:branchId>/change', methods=['POST'])
def change_endpoint(projectId, branchId):
    data = request.get_json()
    
    if not data or 'change_request' not in data:
        return jsonify({'error': 'Invalid request. Missing change_request.'}), 400
    change_request = data['change_request']

    res, code = engine.run(projectId, branchId, change_request)

    return jsonify(res), code

if __name__ == '__main__':
    initialize_logger()
    app.run(debug=True)
