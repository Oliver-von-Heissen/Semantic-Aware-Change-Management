# Semantic-Aware Change Management

A brief description of what this project does and who it's for


## Features

- Light/dark mode toggle
- Live previews
- Fullscreen mode
- Cross platform

## Prerequisites

The following software must be installed on the host machine:
- Docker

## Installation

Then create a python virtual environment using
```bash
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

## Demo

A full demonstration of the semantic-aware change management system can be set up using
```bash
docker compose -f docker-compose.demo.yml up
```
This may take some time for creating the database and service. It is finished, when all docker containers including the frontend are running. Then you can access the user interface at http://localhost:8501/.

Furthermore, the SysML v2 API can then be viewed at http://localhost:9000/docs/.
    
## Usage/Examples

```javascript
import Component from 'my-project'

function App() {
  return <Component />
}
```


## Authors

- Oliver von Heißen