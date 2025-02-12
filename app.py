import os
import tempfile
from flask import Flask, request, jsonify
import docker

app = Flask(__name__)
client = docker.from_env()

@app.route('/', methods=['GET'])
def index():
    return "Server is running!"

@app.route('/build', methods=['POST'])
def build_image():
    """
    Expects a JSON payload:
    {
      "dockerfile": "<Dockerfile>",
      "image_tag": "registry.example.com/myimage:tag"
    }
    """
    data = request.get_json()
    if not data or 'dockerfile' not in data or 'image_tag' not in data:
        return jsonify({'error': 'Missing "dockerfile" or "image_tag" in payload'}), 400

    dockerfile_content = data['dockerfile']
    image_tag = data['image_tag']

    return build_and_push(dockerfile_content, image_tag)

@app.route('/build_file', methods=['POST'])
def build_image_file():
    """
    Accepts a multipart/form-data request with:
    - A file field named 'dockerfile' (the Dockerfile to upload)
    - A form field named 'image_tag'
    """
    if 'dockerfile' not in request.files:
        return jsonify({'error': 'Missing Dockerfile file in request'}), 400

    dockerfile_file = request.files['dockerfile']
    image_tag = request.form.get('image_tag')
    if not image_tag:
        return jsonify({'error': 'Missing "image_tag" in form data'}), 400

    try:
        dockerfile_content = dockerfile_file.read().decode("utf-8")
    except Exception as e:
        return jsonify({'error': f"Error reading file: {e}"}), 400

    return build_and_push(dockerfile_content, image_tag)

def build_and_push(dockerfile_content, image_tag):
    # Create a temporary directory to hold the Dockerfile.
    with tempfile.TemporaryDirectory() as temp_dir:
        dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)

        # Build the Docker image.
        try:
            image, build_logs = client.images.build(path=temp_dir, tag=image_tag, rm=True)
            for chunk in build_logs:
                if isinstance(chunk, bytes):
                    app.logger.info(chunk.decode("utf-8").strip())
                else:
                    app.logger.info(str(chunk))
        except docker.errors.BuildError as e:
            error_message = f"Build failed: {e}"
            app.logger.error(error_message)
            return jsonify({'error': error_message}), 500
        except Exception as e:
            error_message = f"Unexpected error during build: {e}"
            app.logger.error(error_message)
            return jsonify({'error': error_message}), 500

        # Push the image to the registry.
        try:
            push_logs = client.images.push(repository=image_tag, stream=True)
            for line in push_logs:
                if isinstance(line, bytes):
                    app.logger.info(line.decode("utf-8").strip())
                else:
                    app.logger.info(str(line))
        except Exception as e:
            error_message = f"Error pushing image: {e}"
            app.logger.error(error_message)
            return jsonify({'error': error_message}), 500

    return jsonify({'message': 'Image built and pushed successfully', 'image_tag': image_tag}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
