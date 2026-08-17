import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "documents.db")
DOCS_FOLDER = os.path.join(os.path.dirname(__file__), "documents")


def init_db():
    """create chunks and documents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS chunks")
    cursor.execute("""
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_name TEXT,
            section TEXT,
            content TEXT
        )
    """)

    for filename in os.listdir(DOCS_FOLDER):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(DOCS_FOLDER, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Split into chunks by "Article N: Title" pattern
        parts = re.split(r"(Article \d+: [^\n]+)", text)
        parts = [p.strip() for p in parts if p.strip()]

        # parts alternate: [title, body, title, body, ...]
        for i in range(0, len(parts) - 1, 2):
            section_title = parts[i]
            body = parts[i + 1]
            full_content = f"{section_title}\n{body}"
            cursor.execute(
                "INSERT INTO chunks (doc_name, section, content) VALUES (?, ?, ?)",
                (filename, section_title, full_content)
            )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def get_all_chunks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, doc_name, section, content FROM chunks")
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    chunks = get_all_chunks()
    print(f"\nLoaded {len(chunks)} chunks:")
    for c in chunks:
        print(f"  - {c[1]} | {c[2]}")
