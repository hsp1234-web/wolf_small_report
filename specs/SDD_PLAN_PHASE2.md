# Spec-Driven Development Plan (Phase 2 & 3)
# Project: Wolf Small Report (Automated Essay Scoring Pipeline)

## 1. Context & Environment
- **Project Root**: `/home/sp/SP_WORK/wolf_small_report` (Local) or `/content/drive/MyDrive/wolf_small_report` (Colab)
- **Existing Data**:
  - `data/output/links_with_type.csv`: Contains columns `id`, `text`, `link`, `source_type`, `domain`.
  - `data/raw/*.txt`: Original LINE chat logs.
- **Infrastructure Ready**:
  - `src/core/db.py`: SQLite schema and connection logic.
  - `src/core/ollama_client.py`: REST client for Ministral-3b.
  - `config/*.yaml`: Configuration files.

## 2. Objective
Implement the core pipeline to:
1. **Ingest**: Read `links_with_type.csv` and populate the `essays` table in SQLite.
2. **Download**: Fetch content from URLs (GDocs, Drive, Web) and save as local `.txt` files.
3. **Score**: Run a 4-stage LLM evaluation loop (Meta -> Analysis -> Risk -> Summary).

---

## 3. Phase 2 Implementation Tasks (Data Ingestion)

### Task 2.1: Implement `src/orchestrator.py`
**Goal**: Create the entry point for batch processing.

**Requirements**:
- Create a class `Orchestrator`.
- **Method `ingest_csv(csv_path)`**:
  - Read `data/output/links_with_type.csv`.
  - Iterate through rows.
  - Insert into SQLite table `essays` if `link` does not exist.
  - Set default `download_status` to `'pending'`.
  - Map CSV columns: `id` -> `id`, `text` -> `title_text`, `link` -> `link`, `source_type` -> `source_type`.
- **Method `run_batch(step: str, limit: int)`**:
  - Based on `step` ('download', 'meta', etc.), instantiate the corresponding Agent.
  - Call `agent.run(limit)`.

### Task 2.2: Implement `src/agents/download_agent.py`
**Goal**: Download content from URLs to local text files.

**Requirements**:
- Class `DownloadAgent`.
- **Method `run(limit: int)`**:
  - Query DB: `SELECT * FROM essays WHERE download_status='pending' LIMIT {limit}`.
  - Loop through results.
  - **Logic**:
    - If `source_type` == 'gdocs': Construct export URL (`/export?format=txt`).
    - If `source_type` == 'web': Use `requests.get` (basic scraping).
    - Save file to `data/docs/essay_{id}.txt`.
  - **Success**: Update DB `download_status='success'`, `local_path='...'`.
  - **Failure**: Update DB `download_status='failed'`, write to `logs` table.
  - **Constraint**: Do not raise exceptions; catch all errors and log them.

---

## 4. Phase 3 Implementation Tasks (LLM Pipeline)

### Task 3.1: Implement `src/agents/base_agent.py`
**Goal**: Create a base class for all LLM agents to reduce code duplication.

**Requirements**:
- Class `BaseLLMAgent`.
- **Method `_load_text(local_path)`**: Helper to read file content.
- **Method `_call_llm(prompt, system)`**: Wrapper around `OllamaClient`.
- **Method `_parse_json(response)`**: Helper to safely parse JSON from LLM output.

### Task 3.2: Implement Scoring Agents
**Goal**: Implement logic for each scoring round.

1. **`src/agents/meta_agent.py`**:
   - **Input**: `essay_{id}.txt`.
   - **Prompt**: `config/prompts.yaml` -> `meta_round`.
   - **Action**: Extract `target_name`, `target_code`, `topic_type`.
   - **Output**: Update `essay_meta` table. Update `meta_status='done'`.

2. **`src/agents/analysis_agent.py`**:
   - **Input**: Text + Meta info.
   - **Prompt**: `config/prompts.yaml` -> `analysis_round`.
   - **Action**: Evaluate analysis quality (1-5).
   - **Output**: Update `essay_scores` table (`analysis_score`, `analysis_comment`). Update `analysis_status='done'`.

3. **`src/agents/risk_agent.py`**:
   - **Input**: Text.
   - **Prompt**: `config/prompts.yaml` -> `risk_round`.
   - **Output**: Update `essay_scores` table (`risk_score`, `risk_comment`). Update `risk_status='done'`.

4. **`src/agents/summary_agent.py`**:
   - **Input**: Text + Scores.
   - **Prompt**: `config/prompts.yaml` -> `summary_round`.
   - **Output**: Update `essay_outputs` (`short_summary`). Update `summary_status='done'`.

---

## 5. Execution & Verification

### CLI Commands to Implement in `src/main.py`
The AI agent should implement `src/main.py` using `argparse` or `click` to support:

```
# 1. Ingest Data
python src/main.py ingest --file data/output/links_with_type.csv

# 2. Run Download Batch
python src/main.py run --step download --batch-size 10

# 3. Run LLM Scoring Batch
python src/main.py run --step meta --batch-size 5
python src/main.py run --step analysis --batch-size 5
```

### Verification Criteria
- [ ] SQLite database `wolf_small_report.db` is created and populated.
- [ ] `data/docs/` contains downloaded text files.
- [ ] Tables `essay_meta` and `essay_scores` have data after running LLM steps.
- [ ] `logs` table captures any download or parsing errors.
