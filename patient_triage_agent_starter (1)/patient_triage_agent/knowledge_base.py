"""Load public PDF/TXT references, index them in Chroma, and retrieve relevant passages."""
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DB_DIR = BASE_DIR / ".chroma"
COLLECTION = "public_medical_references"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_reference_documents() -> List[Document]:
    DOCS_DIR.mkdir(exist_ok=True)
    loaded: List[Document] = []
    for path in DOCS_DIR.rglob("*"):
        if not path.is_file() or path.name.lower() == "readme.md":
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                docs = PyPDFLoader(str(path)).load()
            elif suffix in {".txt", ".md"}:
                docs = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True).load()
            else:
                continue
            for doc in docs:
                doc.metadata["source"] = path.name
            loaded.extend(docs)
        except Exception as exc:
            print(f"[WARN] Could not load {path.name}: {exc}")
    return loaded

def build_or_load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    existing = list(DB_DIR.glob("*")) if DB_DIR.exists() else []
    if existing:
        return Chroma(
            collection_name=COLLECTION,
            persist_directory=str(DB_DIR),
            embedding_function=embeddings,
        )

    docs = load_reference_documents()
    if not docs:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=850, chunk_overlap=140)
    chunks = splitter.split_documents(docs)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=str(DB_DIR),
    )

def retrieve_reference(query: str, k: int = 3) -> str:
    """Retrieve source-backed snippets; never invent sources if no documents exist."""
    store = build_or_load_vectorstore()
    if store is None:
        return (
            "NO_REFERENCE_DOCUMENTS_FOUND. The docs folder contains no indexed PDF/TXT references. "
            "Do not claim that a medical statement is sourced. Ask the user to add public official references."
        )
    results = store.similarity_search(query, k=k)
    if not results:
        return "No relevant passage was found in the local reference documents."
    parts = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown source")
        page = doc.metadata.get("page")
        page_text = f", page {int(page) + 1}" if isinstance(page, (int, float)) else ""
        parts.append(f"[Reference {i}: {source}{page_text}]\n{doc.page_content}")
    return "\n\n".join(parts)

def reindex_documents() -> str:
    """Delete the local index and rebuild it from current files in docs/."""
    import shutil
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)
    store = build_or_load_vectorstore()
    if store is None:
        return "No PDF/TXT documents found in docs/. Add references and reindex."
    return "Index rebuilt from documents currently in docs/."
