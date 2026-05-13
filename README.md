# NeuroFlow-HiDevs

NeuroFlow is a Retrieval-Augmented Generation (RAG) system designed as part of the HiDevs internship program.  
This project focuses on **system architecture, API contracts, and technology decisions** before implementation.

---

## 📂 Project Structure
NeuroFlow-HiDevs/
├── backend/
├── frontend/
├── pipelines/
├── evaluation/
├── infra/
├── docs/
│   ├── architecture.md
│   ├── api-contracts.md
│   ├── data-models.md
│   └── adr/
│       ├── 001-vector-store.md
│       ├── 002-chunking-strategy.md
│       └── 003-evaluation-framework.md
├── .gitignore
└── README.md


---

## 🚀 Subsystems
- **Ingestion** → Handles raw file/URL input, chunking, embedding, and vector storage.  
- **Retrieval** → Multi-strategy search (embedding, keyword, metadata) with fusion + reranking.  
- **Generation** → Context assembly, LLM routing, streaming responses, logging.  
- **Evaluation** → Automated scoring (faithfulness, relevance, precision, recall) with aggregates.  
- **Fine-Tuning** → Extracts high-quality pairs, formats JSONL, submits jobs, tracks in MLflow.

---

## 🔗 API Endpoints
Defined in `docs/api-contracts.md`:
- `POST /ingest` → File/URL ingestion  
- `POST /query` → RAG query execution  
- `GET /query/{query_id}/stream` → SSE stream  
- `GET /evaluations` → Paginated results  
- `GET /evaluations/aggregate` → Rolling metrics  
- `POST /pipelines` → Create pipeline config  
- `GET /pipelines/{id}/runs` → Pipeline history  
- `POST /finetune/jobs` → Submit fine-tune job  
- `GET /finetune/jobs/{id}` → Job status  
- `GET /health` and `GET /metrics`

---

## 📝 ADRs
Architecture Decision Records (Context → Decision → Consequences):
1. **Vector Store** → Why pgvector over Pinecone/Weaviate/Qdrant.  
2. **Chunking Strategy** → Fixed-size vs sentence vs semantic.  
3. **Evaluation Framework** → Automated LLM-as-judge vs human annotation.  
4. **Model Routing** → Cost, latency, capability, domain-based routing matrix.

---

## ⚙️ Tech Stack
- **Backend** → Python (FastAPI)  
- **Frontend** → React  
- **Vector Store** → Postgres + pgvector  
- **Evaluation DB** → Postgres  
- **Experiment Tracking** → MLflow  
- **Infra** → Docker + Kubernetes

---

## ✅ Status
- Repo is live and Public  
- Branch: `task-31`  
- Documentation complete with architecture, API contracts, data models, ADRs  
- `.gitignore` covers Python, Node, `.env`, caches, DBs, vector store, MLflow logs  

---

## 📌 Submission
(https://github.com/adithiajay06/NeuroFlow-HiDevs/tree/task-31) 
