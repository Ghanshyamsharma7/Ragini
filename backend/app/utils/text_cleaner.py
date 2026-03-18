import re


def clean_ocr_text(text: str) -> str:

    # Remove NCERT reprint watermarks
    text = re.sub(r"Reprint\s*\d{4}-\d{2,4}", "", text, flags=re.IGNORECASE)

    # Remove InDesign file metadata (Chapter 1.indd 1 10/06/2024 11:09)
    text = re.sub(r"Chapter\s*\d+\.indd.*", "", text, flags=re.IGNORECASE)

    # Remove NCERT QR code reference numbers (871CH01, 0871CH06, 671CH01 etc.)
    text = re.sub(r"\b\d{3,4}[A-Z]{2}\d{2,3}\b", "", text)

    # Remove standalone page numbers (single digit or double digit on own line)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Fix broken hyphenated words
    text = re.sub(r"-\n", "", text)

    # Fix words split across lines (e.g. "T\neacher" -> "Teacher")
    text = re.sub(r"([A-Za-z])\n([a-z])", r"\1\2", text)

    # Remove duplicate consecutive lines (repeated headers)
    lines = text.split("\n")
    seen = []
    deduped = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped in seen[-5:]:
            continue
        deduped.append(line)
        if stripped:
            seen.append(stripped)
    text = "\n".join(deduped)

    # Normalize line breaks
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove unwanted characters — preserve full Devanagari block
    text = re.sub(r"[^\w\s.,:;!?()\-\n।॥\u0900-\u097F\u0966-\u096F]", "", text)

    # Remove garbage lines
    cleaned_lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            cleaned_lines.append("")
            continue
        tokens = line.split()
        if not tokens:
            continue
        meaningful = [t for t in tokens if len(t) >= 2]
        has_hindi = any('\u0900' <= ch <= '\u097F' for ch in line)
        ratio = len(meaningful) / len(tokens) if tokens else 0
        if has_hindi or ratio >= 0.4:
            cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Final cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()