# Use the official Python image as a base
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from the requirements.txt file
RUN pip install -r requirements.txt

# Command to run the Streamlit app
CMD ["streamlit", "run", "frontend.py"]