import subprocess
from dotenv import load_dotenv
import os
import sys

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SESSION_SERVICE_URI = os.getenv("SESSION_SERVICE_URI")

REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
REPO_NAME = "travel-agent-service"
IMAGE_NAME = "travel-agent-service"
IMAGE_TAG = "latest"

CLOUDSQL_CONNECTION = f"{PROJECT_ID}:{REGION}:agentdb"

REGISTRY = f"{REGION}-docker.pkg.dev"
FULL_IMAGE = f"{REGISTRY}/{PROJECT_ID}/{REPO_NAME}/{IMAGE_NAME}:{IMAGE_TAG}"
SERVICE_NAME = REPO_NAME

ENV_VARS = ",".join([
    f"GOOGLE_API_KEY={GOOGLE_API_KEY}",
    f"GOOGLE_CLOUD_PROJECT={PROJECT_ID}",
    f"GOOGLE_CLOUD_PROJECT_ID={PROJECT_ID}",
    "GOOGLE_GENAI_USE_VERTEXAI=0",
    "WEB_ALLOWED=True",
    "AIRPORTS_SQLITE_PATH=airports.sqlite",
    "ENABLE_GOOGLE_CLOUD_TRACE=False",
    f"SESSION_SERVICE_URI={SESSION_SERVICE_URI}",
])


def run(label, cmd):
    print(f"\n{label}")
    print(f"  > {' '.join(cmd)}")
    subprocess.run(cmd, shell=True)


skip_build = "--skip-build" in sys.argv

if not skip_build:
    print("\n=== Step 1: Build image and push to Artifact Registry ===")
    exec(open(os.path.join(os.path.dirname(__file__), "build-registry.py")).read())
else:
    print("\n=== Step 1: Skipped (--skip-build) ===")

print("\n=== Step 2: Deploy to Cloud Run ===")
print(f"Deploying {FULL_IMAGE} as service '{SERVICE_NAME}' in {REGION}...")

run(
    "Deploying to Cloud Run...",
    [
        "gcloud", "run", "deploy", SERVICE_NAME,
        f"--image={FULL_IMAGE}",
        f"--region={REGION}",
        f"--project={PROJECT_ID}",
        "--platform=managed",
        "--allow-unauthenticated",
        "--port=8000",
        f"--set-env-vars={ENV_VARS}",
        f"--add-cloudsql-instances={CLOUDSQL_CONNECTION}",
        "--network=default",
        "--subnet=default",
        "--vpc-egress=private-ranges-only",
    ],
)

run(
    "Fetching service URL...",
    [
        "gcloud", "run", "services", "describe", SERVICE_NAME,
        f"--region={REGION}",
        f"--project={PROJECT_ID}",
        '--format=value(status.url)',
    ],
)

print("\nDone!")
