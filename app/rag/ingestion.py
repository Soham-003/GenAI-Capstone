from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.rag.retriever import COLLECTION_NAME


def semantic_chunk(text: str, max_sentences: int = 3) -> list[str]:
    """
    Chunk text by grouping related sentences. Better than fixed-size chunking.
    """
    if not text or not text.strip():
        return []
    
    # Split into sentences while preserving structure
    sentences = []
    current_sent = ""
    
    for char in text:
        current_sent += char
        if char in '.!?':
            stripped = current_sent.strip()
            if stripped:
                sentences.append(stripped)
            current_sent = ""
    
    if current_sent.strip():
        sentences.append(current_sent.strip())
    
    if not sentences:
        return [text] if text.strip() else []
    
    # Group sentences semantically
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i + max_sentences]).strip()
        if chunk:
            chunks.append(chunk)
    
    return chunks


def process_csv_file(csv_path: Path) -> list[str]:
    """Extract meaningful information from CSV files for Q&A system."""
    import pandas as pd
    
    try:
        df = pd.read_csv(csv_path)
        chunks = []
        
        file_name = csv_path.stem
        layer_name = csv_path.parent.name
        
        # Metadata chunk
        metadata_text = f"""Dataset: {file_name}
Layer: {layer_name}
Rows: {df.shape[0]}, Columns: {df.shape[1]}
Schema: {', '.join(df.columns.tolist())}"""
        chunks.append(metadata_text)
        
        # Layer purpose
        layer_descriptions = {
            "bronze": "Raw data layer with unprocessed source data. May contain quality issues and missing values.",
            "silver": "Cleaned data layer. Data is validated, enriched and standardized for analytics.",
            "gold": "Business intelligence layer. Contains aggregated metrics and KPIs ready for reporting."
        }
        
        purpose = layer_descriptions.get(layer_name, "Data layer")
        chunks.append(f"Purpose: {purpose}")
        
        # Table content description
        if "customer" in file_name.lower():
            chunks.append("Contains customer demographic information including contact details and segments.")
        elif "transaction" in file_name.lower():
            chunks.append("Contains transaction records including amounts, timestamps and payment status.")
        elif "product" in file_name.lower():
            chunks.append("Contains product catalog with names, categories, pricing and stock information.")
        
        # Sample data
        if len(df) > 0:
            sample_chunk = "Sample records:\n"
            for idx, row in df.head(2).iterrows():
                sample_chunk += "\n" + "; ".join([f"{col}={val}" for col, val in row.items()])
            chunks.append(sample_chunk)
        
        # Quality metrics
        quality_chunk = "Data quality:\n"
        for col in df.columns:
            null_pct = (df[col].isnull().sum() / len(df)) * 100 if len(df) > 0 else 0
            if df[col].dtype == 'object':
                unique = df[col].nunique()
                quality_chunk += f"\n{col}: {unique} unique values, {null_pct:.1f}% missing"
            else:
                try:
                    quality_chunk += f"\n{col}: {df[col].min()} to {df[col].max()}, {null_pct:.1f}% missing"
                except:
                    quality_chunk += f"\n{col}: {null_pct:.1f}% missing"
        chunks.append(quality_chunk)
        
        return chunks
        
    except Exception as e:
        return [f"Dataset {csv_path.name}: {str(e)}"]


def process_python_file(py_path: Path) -> list[str]:
    """Extract functions, classes and logic from Python source files."""
    try:
        content = py_path.read_text(encoding="utf-8")
        chunks = []
        
        file_name = py_path.name
        try:
            relative_path = py_path.relative_to(Path("app"))
        except:
            relative_path = py_path
        
        chunks.append(f"Module: {relative_path}")
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Class definitions
            if line.startswith('class '):
                class_def = line
                docstring = ""
                if i + 1 < len(lines) and '"""' in lines[i + 1]:
                    j = i + 1
                    doc_lines = []
                    while j < len(lines):
                        doc_lines.append(lines[j])
                        if '"""' in lines[j] and j > i + 1:
                            break
                        j += 1
                    docstring = "\n".join(doc_lines)
                
                chunk_text = f"Class: {class_def}\n{docstring}"
                chunks.append(chunk_text)
            
            # Function definitions
            elif line.startswith('def '):
                func_def = line
                docstring = ""
                if i + 1 < len(lines) and '"""' in lines[i + 1]:
                    j = i + 1
                    doc_lines = []
                    while j < len(lines):
                        doc_lines.append(lines[j])
                        if '"""' in lines[j] and j > i + 1:
                            break
                        j += 1
                    docstring = "\n".join(doc_lines)
                
                chunk_text = f"Function: {func_def}\nDoc: {docstring}"
                chunks.append(chunk_text)
            
            # Comments
            elif line.startswith('#') and not line.startswith('###'):
                chunks.append(f"Note: {line[1:].strip()}")
            
            i += 1
        
        return chunks if chunks else [f"Module: {file_name}"]
        
    except Exception as e:
        return []


def build_index(docs_path: str | None = None, persist_path: str | None = None) -> int:
    """Build knowledge base from docs, datasets and code using semantic chunking."""
    client = chromadb.PersistentClient(path=persist_path or settings.chroma_path)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    docs_to_add: list[str] = []
    ids_to_add: list[str] = []
    metas_to_add: list[dict] = []
    count = 0

    # Index markdown documentation with semantic chunking
    print("Indexing documentation...")
    docs_root = Path(".")
    skip_patterns = [".venv", "__pycache__", ".pytest_cache", "node_modules", ".git", ".egg-info"]
    
    for path in docs_root.rglob("*.md"):
        if any(skip in str(path) for skip in skip_patterns):
            continue
        try:
            raw_text = path.read_text(encoding="utf-8")
            chunks = semantic_chunk(raw_text)
            
            for chunk in chunks:
                if chunk.strip():
                    chunk_id = str(uuid.uuid4())
                    docs_to_add.append(chunk)
                    ids_to_add.append(chunk_id)
                    metas_to_add.append({
                        "source": str(path.relative_to(docs_root)),
                        "type": "documentation"
                    })
                    count += 1
        except:
            pass

    # Index CSV datasets
    print("Indexing datasets...")
    dataset_dir = Path("docs")
    if dataset_dir.exists():
        for path in dataset_dir.rglob("*.csv"):
            try:
                content_chunks = process_csv_file(path)
                for chunk in content_chunks:
                    if chunk.strip():
                        chunk_id = str(uuid.uuid4())
                        docs_to_add.append(chunk)
                        ids_to_add.append(chunk_id)
                        metas_to_add.append({
                            "source": str(path.relative_to(dataset_dir)),
                            "type": "dataset"
                        })
                        count += 1
            except:
                pass

    # Index Python source code
    print("Indexing source code...")
    app_dir = Path("app")
    if app_dir.exists():
        for path in app_dir.rglob("*.py"):
            try:
                content_chunks = process_python_file(path)
                for chunk in content_chunks:
                    if chunk.strip():
                        chunk_id = str(uuid.uuid4())
                        docs_to_add.append(chunk)
                        ids_to_add.append(chunk_id)
                        metas_to_add.append({
                            "source": str(path.relative_to(app_dir)),
                            "type": "code"
                        })
                        count += 1
            except:
                pass

    # Embed and store
    if docs_to_add:
        print(f"Embedding {len(docs_to_add)} chunks...")
        embeddings = model.encode(docs_to_add, show_progress_bar=False).tolist()
        collection.upsert(
            ids=ids_to_add,
            documents=docs_to_add,
            metadatas=metas_to_add,
            embeddings=embeddings
        )

    return count


if __name__ == "__main__":
    total = build_index()
    print(f"Indexed {total} chunks")
