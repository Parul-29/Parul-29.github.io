# Agentic AI DevSecOps Backend

FastAPI backend for a multi-agent DevSecOps pipeline scanner. It coordinates vulnerability, misconfiguration, and compliance agents, deduplicates findings, assigns risk, optionally asks Ollama for reasoning, and exposes a human review queue.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Main Endpoints

```text
POST /api/v1/scans
GET  /api/v1/scans/{scan_id}
GET  /api/v1/review-queue
POST /api/v1/github/webhook
GET  /health
```

## Example Scan Request

```json
{
  "repository": "Parul-29/sample-service",
  "branch": "main",
  "commit_sha": "abc123",
  "changed_files": [
    "app/main.py",
    "requirements.txt",
    "infra/main.tf",
    ".github/workflows/ci.yml"
  ],
  "source_snapshot": {
    "app/main.py": "import subprocess\nsubprocess.call(user_input, shell=True)\n",
    "requirements.txt": "django==2.2.0\nrequests==2.19.0\n",
    "infra/main.tf": "resource \"aws_s3_bucket\" \"logs\" { acl = \"public-read\" }\n"
  }
}
```

## Optional Ollama

The backend works without Ollama. To enable LLM reasoning:

```bash
set OLLAMA_ENABLED=true
set OLLAMA_MODEL=llama3.1
```

Make sure Ollama is running at `http://localhost:11434`.
