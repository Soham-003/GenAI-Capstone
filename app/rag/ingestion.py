from __future__ import annotations

import hashlib
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.rag.retriever import COLLECTION_NAME


def fixed_chunk(text: str, chunk_size: int = 600, overlap: int = 120) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


def semantic_like_chunk(text: str, max_sentences: int = 4) -> list[str]:
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    chunks: list[str] = []
    for i in range(0, len(sentences), max_sentences):
        block = ". ".join(sentences[i : i + max_sentences]).strip()
        if block:
            chunks.append(block + ".")
    return chunks


def hierarchical_chunk(text: str) -> list[str]:
    sections = [s.strip() for s in text.split("##") if s.strip()]
    if not sections:
        return [text]
    return [f"## {section}" for section in sections]


def process_csv_file(csv_path: Path) -> list[str]:
    """Process CSV file and extract meaningful content"""
    import pandas as pd
    
    try:
        df = pd.read_csv(csv_path)
        content_chunks = []
        
        # Add file metadata
        content_chunks.append(f"File: {csv_path.name}")
        content_chunks.append(f"Layer: {csv_path.parent.name}")
        content_chunks.append(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        content_chunks.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Add sample data
        if len(df) > 0:
            content_chunks.append("Sample data:")
            for i, row in df.head(5).iterrows():
                row_data = ", ".join([f"{col}: {val}" for col, val in row.items()])
                content_chunks.append(f"Row {i+1}: {row_data}")
        
        # Add data insights
        content_chunks.append("Data insights:")
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_vals = df[col].nunique()
                content_chunks.append(f"{col}: {unique_vals} unique values")
            else:
                content_chunks.append(f"{col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}")
        
        return content_chunks
        
    except Exception as e:
        return [f"Error processing {csv_path}: {str(e)}"]


def process_python_file(py_path: Path) -> list[str]:
    """Process Python file and extract code documentation"""
    try:
        content = py_path.read_text(encoding="utf-8")
        content_chunks = []
        
        # Add file info
        content_chunks.append(f"File: {py_path.relative_to(py_path.parent.parent)}")
        content_chunks.append(f"Type: Python code")
        
        # Extract docstrings and comments
        lines = content.split('\n')
        in_docstring = False
        docstring_content = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Handle docstrings
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                    docstring_content.append(stripped)
                else:
                    in_docstring = False
                    if docstring_content:
                        content_chunks.append(f"Documentation:\n" + "\n".join(docstring_content))
                        docstring_content = []
                continue
            
            if in_docstring:
                docstring_content.append(stripped)
                continue
            
            # Extract comments and function/class definitions
            if stripped.startswith('#'):
                content_chunks.append(f"Comment: {stripped[1:].strip()}")
            elif stripped.startswith('def ') or stripped.startswith('class '):
                content_chunks.append(f"Code: {stripped}")
        
        return content_chunks
        
    except Exception as e:
        return [f"Error processing {py_path}: {str(e)}"]


def build_index(docs_path: str | None = None, persist_path: str | None = None) -> int:
    # Process documentation files
    docs_dir = Path(docs_path or settings.docs_path)
    if not docs_dir.exists():
        # If data/docs doesn't exist, use root for MD files
        docs_dir = Path(".")

    client = chromadb.PersistentClient(path=persist_path or settings.chroma_path)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    docs_to_add: list[str] = []
    ids_to_add: list[str] = []
    metas_to_add: list[dict] = []
    count = 0

    # Process markdown documentation files
    docs_root = Path(".")
    for path in docs_root.rglob("*.md"):
        if ".venv" in str(path) or "__pycache__" in str(path):
            continue
        raw_text = path.read_text(encoding="utf-8")
        chunks = fixed_chunk(raw_text) + semantic_like_chunk(raw_text) + hierarchical_chunk(raw_text)
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.sha256(f"doc_{path}:{i}:{chunk}".encode("utf-8")).hexdigest()[:16]
            docs_to_add.append(chunk)
            ids_to_add.append(chunk_id)
            metas_to_add.append({"source": str(path.relative_to(docs_root)), "type": "documentation"})
            count += 1

    # Process CSV dataset files
    dataset_dir = Path("docs")
    for path in dataset_dir.rglob("*.csv"):
        content_chunks = process_csv_file(path)
        for i, chunk in enumerate(content_chunks):
            chunk_id = hashlib.sha256(f"csv_{path}:{i}:{chunk}".encode("utf-8")).hexdigest()[:16]
            docs_to_add.append(chunk)
            ids_to_add.append(chunk_id)
            metas_to_add.append({"source": str(path.relative_to(dataset_dir)), "type": "dataset"})
            count += 1

    # Process Python code files
    app_dir = Path("app")
    for path in app_dir.rglob("*.py"):
        content_chunks = process_python_file(path)
        for i, chunk in enumerate(content_chunks):
            chunk_id = hashlib.sha256(f"code_{path}:{i}:{chunk}".encode("utf-8")).hexdigest()[:16]
            docs_to_add.append(chunk)
            ids_to_add.append(chunk_id)
            metas_to_add.append({"source": str(path.relative_to(app_dir)), "type": "code"})
            count += 1

    if docs_to_add:
        embeddings = model.encode(docs_to_add).tolist()
        collection.upsert(ids=ids_to_add, documents=docs_to_add, metadatas=metas_to_add, embeddings=embeddings)

    return count


if __name__ == "__main__":
    total = build_index()
    print(f"Indexed {total} chunks")
