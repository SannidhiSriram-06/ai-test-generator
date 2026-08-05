# AI Test Generator

> A DevOps/Cloud engineering project: a containerized FastAPI microservice with CI, a GitOps chart repository, and Kubernetes deployment configuration. The service calls an LLM to generate pytest suites; the main focus is the delivery workflow around it — automated testing, a coverage gate, versioned image tags, and GitOps-oriented deployment.

---

## 🏗️ Architecture

**Flow:**

Developer Push → Jenkins CI (test + coverage gate) → AWS ECR → GitOps repo (`values.yaml` update) → ArgoCD sync → Kubernetes (Minikube)

**Key Components:**

* Jenkins CI pipeline (build, test, coverage gate, image push)
* AWS ECR (container registry)
* Terraform (ECR provisioning, IaC)
* [ai-pytest-generator-gitops](https://github.com/SannidhiSriram-06/ai-pytest-generator-gitops) — deployment-state repo (Helm chart)
* ArgoCD (continuous delivery / GitOps reconciliation)
* Kubernetes (Minikube), Helm
* FastAPI microservice (the application being deployed)

---

## ⚙️ Tech Stack

| Layer            | Technology                  |
| ---------------- | ---------------------------- |
| CI/CD            | Jenkins                     |
| Containerization | Docker (multi-stage build)  |
| Registry         | AWS ECR                     |
| IaC              | Terraform                   |
| GitOps           | ArgoCD                      |
| Orchestration    | Kubernetes (Minikube), Helm |
| Backend          | FastAPI (Python 3.11)       |
| AI/LLM           | Groq API (LLaMA 3.1)        |

---

## 🔄 CI/CD Pipeline

The `Jenkinsfile` defines the following pipeline stages. Repository triggers (for example, a GitHub webhook) are configured outside this repository.

| Stage | What happens |
|---|---|
| **Checkout** | Jenkins pulls the latest commit |
| **Install dependencies** | `pip install` into a virtualenv |
| **Run tests** | `pytest --cov=app --cov-fail-under=70` — build fails if coverage drops below 70% |
| **Build & push to ECR** | Docker image built, tagged `BUILD_NUMBER-COMMIT_SHA`, pushed to AWS ECR (`ap-south-1`) |
| **Update GitOps repo** | Jenkins attempts to clone `ai-test-generator-gitops`, updates `image.tag` in `charts/ai-test-generator/values.yaml`, commits, pushes. This URL currently differs from the companion repository's configured origin (`ai-pytest-generator-gitops`). |
| **GitOps reconciliation** | An externally configured Argo CD application can detect the `values.yaml` change and sync the rendered manifests to its target cluster |

The pipeline references Jenkins credential IDs for AWS credentials, the Groq API key, and a GitHub token. The repository configuration contains no secret values; keep deployment screenshots and other artifacts free of credentials as well.

---

## ☁️ Deployment Model

* Application containerized (`Dockerfile`, non-root user, multi-stage build) and deployed on Kubernetes (Minikube)
* Helm chart configuration lives in the companion GitOps repo
* Argo CD reconciliation and the target-cluster setup are external to these repositories
* ECR repository and lifecycle policy (keep last 10 images, scan-on-push) provisioned via Terraform (`Terraform/main.tf`)

The ECR repository is configured as **mutable** and the pipeline also pushes `latest`; the build-specific `BUILD_NUMBER-COMMIT_SHA` tag is the tag written to the GitOps values file.

---

## 🧠 The Application (what actually gets deployed)

A FastAPI microservice that generates pytest test suites from Python source code using Groq's LLM API. This is the workload the pipeline above builds, tests, and ships — not the focus of the project, but useful context for what the pods are running.

**Endpoints:**

* `POST /generate` — accepts `{"code": "..."}`, validates input (non-empty, ≤2000 chars), rate-limited to 5 requests/minute (`slowapi`), sends the code to Groq's `llama-3.1-8b-instant` model with a structured prompt, returns a generated pytest file
* `GET /health` — application health endpoint
* `GET /metrics` — in-memory request/error counters

---

## 📁 Project Structure

```
ai-test-generator/
├── app/
│   ├── __init__.py
│   ├── config.py          # reserved module (currently empty)
│   └── main.py            # FastAPI app: /health, /metrics, /generate
├── tests/
│   └── test_main.py       # async pytest tests (httpx + mocked Groq client)
├── Terraform/
│   └── main.tf            # ECR repo + lifecycle policy (ap-south-1)
├── Dockerfile              # multi-stage build, python:3.11-slim, non-root user
├── Jenkinsfile              # CI pipeline (pytest → ECR → gitops update)
├── pytest.ini               # asyncio_mode = auto
├── requirements.txt
└── README.md
```

---

## 💻 Local Setup

### Prerequisites

* Python 3.11+
* Docker
* A [Groq API key](https://console.groq.com/)

### Steps

```bash
git clone https://github.com/SannidhiSriram-06/ai-test-generator.git
cd ai-test-generator

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env

uvicorn app.main:app --reload --port 8000
```

API runs at `http://localhost:8000`.

### Usage

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b):\n    return a + b"}'
```

---

## 🔬 Testing

```bash
pytest tests/ --cov=app --cov-fail-under=70 -v
```

The Jenkins test stage enforces the 70% threshold before image build and GitOps-update stages. Run the command locally after installing the development dependencies.

---

## 🔐 Security Considerations

* The text configuration references Jenkins credential IDs rather than secret values
* The Kubernetes chart expects pre-existing `ecr-secret` and `ai-test-generator-secret` secrets
* Non-root container user
* Input validation before LLM invocation
* CI-integrated coverage gate as a quality safeguard

---

## 🎯 Objectives

This project demonstrates:

* CI/CD pipeline design with enforced quality gates (Jenkins)
* GitOps deployment automation (ArgoCD + Helm)
* Infrastructure as Code (Terraform)
* Container image lifecycle management (ECR lifecycle policy and versioned build tags)
* Running containerized workloads on Kubernetes
* Integrating a third-party LLM API behind a rate-limited FastAPI service

---

## 📌 Notes

`Deployment-Screenshots.pdf` contains historical validation screenshots. Review and redact any sensitive values before sharing it.

---

## License

No license file is currently included in this repository.
