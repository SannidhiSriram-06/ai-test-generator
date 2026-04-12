# AI Test Generator

> A FastAPI-based microservice that generates executable pytest test suites from Python code using LLM inference, deployed via a fully automated GitOps CI/CD pipeline.

---

## 🧠 Overview

This system automates test generation by converting raw Python functions into structured pytest suites using a large language model. The service is designed with a production-style delivery pipeline, including automated testing, containerization, and GitOps-based deployment.

**Core capabilities:**

* LLM-driven test generation from source code
* API-based interaction with validation and rate limiting
* Automated CI/CD with coverage enforcement
* GitOps-driven deployment to a Kubernetes environment

---

## 🏗️ Architecture

**Flow:**

Developer Push → CI Pipeline → Container Registry → GitOps Repo → ArgoCD → Kubernetes Cluster

**Key Components:**

* FastAPI microservice (test generation engine)
* Jenkins CI pipeline (build, test, security gates)
* AWS ECR (container registry)
* GitOps repository (deployment state)
* ArgoCD (continuous delivery)
* Kubernetes (Minikube) runtime

---

## ⚙️ Tech Stack

| Layer            | Technology                  |
| ---------------- | --------------------------- |
| Backend          | FastAPI (Python 3.11)       |
| AI/LLM           | Groq API (LLaMA 3.1)        |
| CI/CD            | Jenkins                     |
| Containerization | Docker                      |
| Orchestration    | Kubernetes (Minikube), Helm |
| GitOps           | ArgoCD                      |
| Registry         | AWS ECR                     |
| IaC              | Terraform                   |

---

## 🚀 Functionality

1. Client sends Python code to `/generate` endpoint
2. Service validates input (size, format, rate limits)
3. Code is passed to Groq LLM with structured prompt
4. LLM returns a complete pytest test suite
5. Response is returned as executable test code

**Additional controls:**

* Rate limiting: 5 requests/minute (`slowapi`)
* Input validation for robustness
* Health endpoint for monitoring

---

## 🧩 System Behavior

* Test generation is deterministic at API level (validated inputs, structured prompts)
* CI enforces a **minimum 70% coverage gate** before deployment
* Each build produces a uniquely tagged container image
* Deployment is fully automated via GitOps synchronization

---

## 📁 Project Structure

```id="s4yr3m"
ai-test-generator/
├── app/
├── tests/
├── terraform/
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── README.md
```

---

## 💻 Local Setup

### Prerequisites

* Python 3.11+
* Docker
* Groq API key

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

API runs at: `http://localhost:8000`

---

## 🔬 Testing

```bash
pytest tests/ --cov=app --cov-fail-under=70 -v
```

* Coverage threshold enforced both locally and in CI
* Ensures deployment only occurs for validated builds

---

## 🔄 CI/CD Pipeline

Triggered on every push to `main`.

**Pipeline stages:**

1. Checkout code
2. Install dependencies
3. Run tests with coverage gate
4. Build Docker image
5. Push image to AWS ECR
6. Update GitOps repository (`values.yaml`)
7. ArgoCD sync triggers deployment

**Key characteristics:**

* Fail-fast on test or coverage failure
* Immutable image tagging (`BUILD_NUMBER-COMMIT_SHA`)
* Separation of application and deployment state

---

## ☁️ Deployment Model

* Application containerized and deployed on Kubernetes (Minikube)
* Helm manages release configuration
* ArgoCD continuously reconciles desired state from GitOps repo

A complete deployment workflow is implemented and documented within the repository, enabling reproducible setup of the full pipeline.

> The system was deployed and validated as part of project execution.
> Infrastructure resources were decommissioned after validation to optimize cost usage.
> All configuration and deployment steps are preserved for reproducibility.

---

## 🔐 Security Considerations

* No credentials stored in source code
* Secrets managed via Jenkins credential store
* Input validation before LLM invocation
* CI-integrated safeguards (coverage gate)

---

## 🎯 Objectives

This project demonstrates:

* Practical use of LLMs in developer tooling
* Designing API-driven AI microservices
* Implementing CI/CD with enforced quality gates
* Applying GitOps principles for deployment automation
* Managing containerized workloads in Kubernetes

---

## 🏁 Outcome

A fully automated system that:

* Generates test cases from code using LLM inference
* Enforces quality through CI pipelines
* Deploys continuously using GitOps principles

This project represents a production-style implementation of an **AI-assisted developer tooling system with automated delivery pipelines**.

---

## 📌 Notes

The deployment pipeline and infrastructure were actively used during development and validation. Resources were later decommissioned to optimize cost usage, while preserving full reproducibility through configuration and documentation.

---

## License

MIT
