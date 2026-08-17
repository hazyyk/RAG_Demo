from database import get_all_chunks

CONFIDENCE_THRESHOLD = 0.55  # if best match score is below this, we abstain

STOPWORDS = {
    "what", "is", "the", "a", "an", "for", "of", "to", "in", "on", "how",
    "are", "does", "do", "and", "or", "be", "can", "will", "shall", "this",
    "that", "under", "with", "at", "by", "as", "it", "its",
    # domain-specific words that appear in almost every article in this
    # corpus, so they don't help distinguish one topic from another
    "tax", "goods", "import", "export", "imported", "exported", "vietnam"
}


def simple_score(question, chunk_text):
    """
    Simple keyword overlap score, ignoring common stopwords so filler
    words like "the" and "is" don't create false matches.
    Good enough for a small demo - can be swapped for embeddings later.
    """
    question_words = set(question.lower().replace("?", "").split()) - STOPWORDS
    chunk_words = set(chunk_text.lower().replace(".", "").replace(",", "").split()) - STOPWORDS

    if not question_words:
        return 0.0

    overlap = question_words & chunk_words
    return len(overlap) / len(question_words)


def retrieve_best_match(question):
    """
    Search all chunks, return the best match plus a confidence decision.
    Returns a dict with: found (bool), doc_name, section, content, score
    """
    chunks = get_all_chunks()

    best_score = 0.0
    best_chunk = None

    for chunk_id, doc_name, section, content in chunks:
        score = simple_score(question, content)
        if score > best_score:
            best_score = score
            best_chunk = (doc_name, section, content)

    if best_score < CONFIDENCE_THRESHOLD or best_chunk is None:
        return {
            "found": False,
            "score": round(best_score, 3)
        }

    doc_name, section, content = best_chunk
    return {
        "found": True,
        "doc_name": doc_name,
        "section": section,
        "content": content,
        "score": round(best_score, 3)
    }


if __name__ == "__main__":
    test_questions = [
        "How is customs value converted to Vietnamese Dong?",
        "What is the time limit for paying export tax?",
        "What is the tax rate for coffee exports?",  # should NOT be found
        "What is the tax exemption threshold for gifts to individuals?",
    ]

    for q in test_questions:
        result = retrieve_best_match(q)
        print(f"\nQ: {q}")
        if result["found"]:
            print(f"  MATCH (score={result['score']}) -> {result['doc_name']} / {result['section']}")
        else:
            print(f"  NOT FOUND (best score={result['score']}) -> would say 'not found in documents'")
