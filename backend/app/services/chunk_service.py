import re


def semantic_chunk_text(text: str, chunk_size: int = 200, overlap: int = 50):
    """
    Fixed-size chunking with overlap.
    
    chunk_size : target words per chunk (200 = good for NCERT Q&A)
    overlap    : words shared between consecutive chunks (prevents
                 answers being split at chunk boundaries)
    
    Example with chunk_size=200, overlap=50:
      Chunk 1: words   0-200
      Chunk 2: words 150-350
      Chunk 3: words 300-500
    """

    # Clean up extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Split into words
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        # Take chunk
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)

        if chunk.strip():
            chunks.append(chunk.strip())

        # Move forward by (chunk_size - overlap)
        # This creates the overlap between consecutive chunks
        start += chunk_size - overlap

        # Safety: if overlap >= chunk_size, avoid infinite loop
        if chunk_size <= overlap:
            break

    return chunks