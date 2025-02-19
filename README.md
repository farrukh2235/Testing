# Docker Builder Service

This is a simple RESTful service that accepts a Dockerfile, builds a Docker image, and pushes it to a Docker registry.
### Prerequisites
- Ensure **Docker** is installed on your system.
- Ensure **Python** is installed along with the necessary dependencies.

### Steps to Follow

1. **Install Required Dependencies**  
   Upgrade and install necessary Python packages:
   ```bash
   pip install --upgrade -r req.txt
   ```

2. **Start Docker**  
   If Docker is not running, start it before proceeding.

3. **Log in to Docker Registry**  
   Run the following command and enter your credentials when prompted:
   ```bash
   docker login
   ```

4. **Run the Python Application**  
   Start the application:
   ```bash
   python app.py
   ```

5. **Build and Push Docker Image using API**  
   Use `curl` to trigger the build via API:
   ```bash
   curl -X POST http://localhost:5000/build_file \
        -F "dockerfile=@Dockerfile" \
        -F "image_tag=docker.io/farrukhvirk/aicore-berlin:latest"
   ```

### Notes
- Ensure the `Dockerfile` is in the correct directory before running the `curl` command.
- Replace `docker.io/farrukhvirk/myimage:latest` with your own image tag if needed.
- If pushing to a private registry, make sure you have the correct authentication and repository permissions.
