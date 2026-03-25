import subprocess
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
REPO_NAME = "travel-agent-service"
IMAGE_NAME = "travel-agent-service"
IMAGE_TAG = "latest"

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
])


def run(label, cmd):
    print(f"\n{label}")
    print(f"  > {' '.join(cmd)}")
    subprocess.run(cmd, shell=True)


print("\n=== Step 1: Build image and push to Artifact Registry ===")
exec(open("build-registry.py").read())

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
