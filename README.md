# Docker Builder Service

This is a simple RESTful service that accepts a Dockerfile, builds a Docker image, and pushes it to a Docker registry.

## Prerequisites

- Python 3.8+
- Docker installed and running on the same machine as this service.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/docker-builder-service.git

## Running
- pip install --upgrade -r req.txt
- python app.py
- curl -X POST http://localhost:5000/build_file \
  -F "dockerfile=@Dockerfile" \
  -F "image_tag=docker.io/farrukhvirk/myimage:latest"
