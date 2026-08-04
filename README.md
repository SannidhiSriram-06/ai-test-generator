# AI Test Generator

> A DevOps/Cloud engineering project: a containerized FastAPI microservice with a full CI/CD → GitOps → Kubernetes delivery pipeline. The service itself happens to call an LLM to generate pytest suites, but the point of the project is the pipeline around it — automated testing, coverage gating, immutable image builds, and GitOps-driven deployment.

---

## 🏗️ Architecture

**Flow:**

Developer Push → Jenkins CI (test + coverage gate) → AWS ECR → GitOps repo (`values.yaml` update) → ArgoCD sync → Kubernetes (Minikube)

**Key Components:**

* Jenkins CI pipeline (build, test, coverage gate, image push)
* AWS ECR (container registry)
* Terraform (ECR provisioning, IaC)
* [ai-test-generator-gitops](https://github.com/SannidhiSriram-06/ai-pytest-generator-gitops) — deployment-state repo (Helm chart)
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

Triggered on every push to `main` (see `Jenkinsfile`).

| Stage | What happens |
|---|---|
| **Checkout** | Jenkins pulls the latest commit |
| **Install dependencies** | `pip install` into a virtualenv |
| **Run tests** | `pytest --cov=app --cov-fail-under=70` — build fails if coverage drops below 70% |
| **Build & push to ECR** | Docker image built, tagged `BUILD_NUMBER-COMMIT_SHA`, pushed to AWS ECR (`ap-south-1`) |
| **Update GitOps repo** | Jenkins clones `ai-pytest-generator-gitops`, updates `image.tag` in `charts/ai-test-generator/values.yaml`, commits, pushes |
| **ArgoCD sync** | ArgoCD detects the `values.yaml` change and rolls out the new image on Minikube automatically |

Secrets (AWS credentials, Groq API key, GitHub PAT) are stored in the Jenkins credential store — never in code.

---

## ☁️ Deployment Model

* Application containerized (`Dockerfile`, non-root user, multi-stage build) and deployed on Kubernetes (Minikube)
* Helm manages release configuration via the companion GitOps repo
* ArgoCD continuously reconciles cluster state from the GitOps repo — no manual `kubectl apply`
* ECR repository and lifecycle policy (keep last 10 images, scan-on-push) provisioned via Terraform (`Terraform/main.tf`)

> The system was deployed and validated end-to-end (Jenkins → ECR → ArgoCD → Minikube) as part of project execution.
> Infrastructure resources were decommissioned afterward to optimize cost usage. All configuration is preserved for reproducibility.

---

## 🧠 The Application (what actually gets deployed)

A FastAPI microservice that generates pytest test suites from Python source code using Groq's LLM API. This is the workload the pipeline above builds, tests, and ships — not the focus of the project, but useful context for what the pods are running.

**Endpoints:**

* `POST /generate` — accepts `{"code": "..."}`, validates input (non-empty, ≤2000 chars), rate-limited to 5 requests/minute (`slowapi`), sends the code to Groq's `llama-3.1-8b-instant` model with a structured prompt, returns a generated pytest file
* `GET /health` — liveness/health check
* `GET /metrics` — in-memory request/error counters

---

## 📁 Project Structure

```
ai-test-generator/
├── app/
│   ├── __init__.py
│   ├── config.py          # env var loading
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

Coverage threshold (70%) is enforced both locally and in CI — deployment only happens for builds that pass it.

---

## 🔐 Security Considerations

* No credentials stored in source code
* Secrets managed via Jenkins credential store
* Non-root container user
* Input validation before LLM invocation
* CI-integrated coverage gate as a quality safeguard

---

## 🎯 Objectives

This project demonstrates:

* CI/CD pipeline design with enforced quality gates (Jenkins)
* GitOps deployment automation (ArgoCD + Helm)
* Infrastructure as Code (Terraform)
* Container image lifecycle management (ECR, immutable tagging)
* Running containerized workloads on Kubernetes
* Integrating a third-party LLM API behind a rate-limited FastAPI service

---

## 📌 Notes

See `Deployment-Screenshots.pdf` in this repository for the Jenkins build, ArgoCD sync status, and kubectl pod output captured during validation.

---

## License

MIT
