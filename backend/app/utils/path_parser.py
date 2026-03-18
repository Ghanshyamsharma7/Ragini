def parse_supabase_path(file_path: str):
    """
    Extract class, subject, chapter from file path.
    Example:
    class_10/science/ch_01.pdf
    """
    parts = file_path.split("/")

    class_name = parts[0]
    subject = parts[1]
    chapter = parts[2].replace(".pdf", "")

    return class_name, subject, chapter