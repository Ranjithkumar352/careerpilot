import re


def chunk_resume(text):
    """
    Split a resume into meaningful section-based chunks.
    """

    sections = re.split(
        r"\n(?=[A-Z][A-Za-z ]{2,30}:)",
        text.strip()
    )

    chunks = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.split("\n")

        first_line = lines[0].strip()

        # If the first line looks like:
        # Technical Skills:
        # Experience:
        # Projects:
        if first_line.endswith(":"):
            section_name = first_line[:-1].strip()
            content = "\n".join(lines[1:]).strip()
        else:
            section_name = "General"
            content = section

        if content:
            chunks.append({
                "section": section_name,
                "text": content
            })

    return chunks