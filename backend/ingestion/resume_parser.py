import re


SECTION_ALIASES = {
    "about": [
        "ABOUT ME",
        "SUMMARY",
        "PROFESSIONAL SUMMARY",
        "PROFILE",
        "OBJECTIVE",
    ],

    "highlights": [
        "RESULTS AT A GLANCE",
        "HIGHLIGHTS",
        "KEY HIGHLIGHTS",
    ],

    "strengths": [
        "WHAT I'M GOOD AT",
        "KEY STRENGTHS",
        "CORE STRENGTHS",
    ],

    "experience": [
        "WORK EXPERIENCE",
        "EXPERIENCE",
        "PROFESSIONAL EXPERIENCE",
        "EMPLOYMENT HISTORY",
    ],

    "projects": [
        "PROJECTS",
        "PERSONAL PROJECTS",
        "ACADEMIC PROJECTS",
    ],

    "skills": [
        "SKILLS",
        "TECHNICAL SKILLS",
        "TECHNOLOGIES",
    ],

    "education": [
        "EDUCATION",
        "ACADEMIC QUALIFICATIONS",
    ],

    "certifications": [
        "CERTIFICATIONS",
        "CERTIFICATES",
    ],

    "additional_experience": [
        "STARTUP PRODUCT ENGINEERING EXPOSURE",
        "ADDITIONAL EXPERIENCE",
        "OTHER EXPERIENCE",
    ],
}


def normalize_heading(line):
    """
    Normalize a possible resume heading.
    """

    line = line.strip()

    # Remove extra spaces
    line = re.sub(r"\s+", " ", line)

    # Convert to uppercase for comparison
    return line.upper()


def detect_section(line):
    """
    Check whether a line represents a known resume section.
    """

    normalized = normalize_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section_name

    return None


def parse_resume_sections(text):
    """
    Parse extracted resume text into logical sections.
    """

    lines = text.splitlines()

    sections = {}
    current_section = "personal"

    sections[current_section] = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        detected_section = detect_section(line)

        if detected_section:
            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    # Convert lists into strings
    for section_name in sections:
        sections[section_name] = "\n".join(
            sections[section_name]
        ).strip()

    # Remove empty sections
    sections = {
        key: value
        for key, value in sections.items()
        if value
    }

    return sections


if __name__ == "__main__":

    from pdf_parser import extract_text_from_pdf

    pdf_path = "resume.pdf"

    text = extract_text_from_pdf(pdf_path)

    sections = parse_resume_sections(text)

    print("\n==============================")
    print("STRUCTURED RESUME")
    print("==============================")

    for section_name, content in sections.items():

        print(f"\n--- {section_name.upper()} ---")
        print(content)

    print("\n==============================")
    print("RESUME STRUCTURED SUCCESSFULLY")
    print("==============================")