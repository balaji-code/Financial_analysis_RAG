import re

def split_into_paragraphs(mda_pages, sentences_per_chunk=4):
    """
    Create pseudo-paragraphs by grouping sentences.
    """
    paragraphs = []

    for page_no, text in mda_pages:
        # Clean whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', cleaned)

        # Group sentences into chunks
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = " ".join(sentences[i:i+sentences_per_chunk]).strip()

            if len(chunk) < 120:
                continue

            paragraphs.append({
                "page_no": page_no,
                "paragraph": chunk
            })

    return paragraphs