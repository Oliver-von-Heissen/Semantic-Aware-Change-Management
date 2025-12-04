# Semantic-Aware Change Management

The project Semantic-Aware Change Management demonstrates a concept for minimal controlled change requests on SysML v2 models. 
The application
- Receives a high level change request (e.g. "Rename my element from X to Y")
- Extracts a minimal context from the SysML model using the SysML v2 API
- Suggests a set of atomic operations (create, update, delete)
- Validates the atomic operations syntactically and semantically
- Applies the operations on the model with versioning

## Prerequisites

The following software must be installed on the host machine:
- Docker

## Demo

### Preparation

For the demo, an environment file has to be created and placed in `demo` which requires the following fields:

```
POSTGRES_DB=sysml2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
SYSML_API_URL=http://sysml-api:9000
CHANGE_ENGINE_URL=http://change-engine:8000
OPENAI_API_KEY=xxx
```

Here, the OpenAI API key has to be entered to enable access.

### Setup

A full demonstration of the semantic-aware change management system can be set up using
```bash
docker compose -f docker-compose.demo.yml up
```
This may take some time for creating the database and service. It is finished, when all docker containers including the frontend are running. Then you can access the user interface at http://localhost:8501/.

Furthermore, the SysML v2 API can then be viewed at http://localhost:9000/docs/.

## Development

Create a python virtual environment using
```bash
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

## Authors

- Oliver von Heißen
- Kenneth Tagscherer