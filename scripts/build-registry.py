import subprocess
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
REPO_NAME = "travel-agent-service"
IMAGE_NAME = "travel-agent-service"
IMAGE_TAG = "latest"

REGISTRY = f"{REGION}-docker.pkg.dev"
FULL_IMAGE = f"{REGISTRY}/{PROJECT_ID}/{REPO_NAME}/{IMAGE_NAME}:{IMAGE_TAG}"


def run(label, cmd):
    print(f"\n{label}")
    print(f"  > {' '.join(cmd)}")
    subprocess.run(cmd, shell=True)


run(
    "[1/4] Setting active GCP project...",
    ["gcloud", "config", "set", "project", PROJECT_ID],
)

run(
    "[2/4] Creating Artifact Registry repository...",
    [
        "gcloud", "artifacts", "repositories", "create", REPO_NAME,
        "--repository-format=docker",
        f"--location={REGION}",
        f"--description=Docker repository for {IMAGE_NAME}",
    ],
)

run(
    "[3/4] Configuring Docker authentication...",
    ["gcloud", "auth", "configure-docker", REGISTRY, "--quiet"],
)

run(
    "[4/4] Building Docker image...",
    ["docker", "build", "-t", FULL_IMAGE, "-f", "dockerfile", "."],
)

run(
    "[4/4] Pushing Docker image...",
    ["docker", "push", FULL_IMAGE],
)

print(f"\nDone! Image available at:\n  {FULL_IMAGE}")
