FROM python:3.13-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die Anforderungen in das Arbeitsverzeichnis
COPY requirements.txt .

# Installiere die Anforderungen
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten Anwendungscode in das Arbeitsverzeichnis
COPY . .

# Exponiere den Port, auf dem die App läuft
EXPOSE 8000

# Starte die Anwendung mit Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
