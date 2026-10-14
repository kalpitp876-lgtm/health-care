# Patient Triage & Reference Assistant

A local educational prototype based on the requested workflow:
1. User asks about a symptom or medication.
2. Retrieve matching passages from public reference documents.
3. For symptoms, run deterministic Python keyword rules (not LLM judgement).
4. If a clinician review or urgent result is returned, map to a department using a fixed Python lookup.
5. Present a grounded answer in a Streamlit chat UI.

## Requirements
- Windows 10/11, macOS, or Linux
- Python 3.11 or 3.12 recommended
- Ollama installed and running
- Internet access for the initial Python package/model downloads

## 1. Open this folder in Antigravity
Create/open the `patient_triage_agent` folder as your project.

## 2. Create and activate a virtual environment (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt instead:
```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Install and start Ollama
Install from https://ollama.com/download and then in a terminal:
```powershell
ollama pull qwen3:0.6b
ollama run qwen3:0.6b
```
After you see the model respond, type `/bye` to exit. Keep Ollama running in the background. If this small model is too weak, try `ollama pull qwen3:4b` and set `OLLAMA_MODEL=qwen3:4b` before launching the app (requires more RAM).

## 4. Add references
Download public, non-patient-specific PDF or TXT references from official sources such as national health agencies or official medication leaflets, respecting their terms. Put them in `docs/`.
Do not use patient records. Check the actual source and publication date before relying on a document. This starter does not automatically download or validate medical sources.

## 5. Run the app
```powershell
streamlit run app.py
```
Open the local URL printed in the terminal (usually http://localhost:8501).

## 6. Run quick checks
```powershell
python -c "from tools import classify_triage, find_specialist; print(classify_triage('I have chest pain')); print(find_specialist('chest pain','urgent'))"
python -c "from knowledge_base import retrieve_reference; print(retrieve_reference('medicine side effects'))"
```

## Project structure
```text
patient_triage_agent/
├── app.py
├── agent.py
├── tools.py
├── knowledge_base.py
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
│   └── README.md
└── .chroma/            # created locally after indexing
```

## Troubleshooting
- `ollama: command not found`: install Ollama and reopen the terminal.
- Model connection error: run `ollama list`; make sure the model is downloaded and Ollama is running.
- First embedding/index run is slow: the sentence-transformer model downloads once.
- No sources found: add PDF/TXT files to `docs/`, then click **Rebuild reference index**.
- Updated or removed documents: click **Rebuild reference index** so the local index is recreated.
- Windows activation policy error: use Command Prompt activation, or review your PowerShell execution policy with your administrator.
- Package compatibility errors: use Python 3.11/3.12 in a fresh `.venv` and reinstall requirements.

## Important limitations
- The triage keyword rules are a demonstration only, not a validated medical protocol; they can miss important symptoms and context.
- The specialist mapping is also a small example table, not a clinical referral standard.
- Do not deploy for real patients without clinical review, extensive safety testing, privacy/security review, and appropriate regulatory assessment.
