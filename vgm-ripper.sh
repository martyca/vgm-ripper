#!/usr/bin/env bash
# 
# This script checks if the Docker image "vgm-ripper" exists;
# if not, it prints an error and exits.

IMAGE_NAME="vgm-ripper"

# Using "docker image inspect" to see if the image exists
# Redirecting output to /dev/null to avoid cluttering the console
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
  echo "Error: Docker image '$IMAGE_NAME' does not exist. Run 'build-container.sh' to create the image. Exiting."
  exit 1
fi

echo "Docker image '$IMAGE_NAME' exists. Continuing..."

# Run container
echo add "--quality high" parameter to download higher quality files if they exist.

docker run -t -v "$(pwd)":/downloads "$IMAGE_NAME" "$@"
