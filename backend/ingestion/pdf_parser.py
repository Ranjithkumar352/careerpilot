from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """
    Extract text from all pages of a PDF resume.
    """

    reader = PdfReader(file_path)

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    full_text = "\n".join(extracted_text)

    return full_text.strip()


if __name__ == "__main__":
    pdf_path = "resume.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("\n==============================")
    print("RESUME TEXT")
    print("==============================\n")

    print(text)

    print("\n==============================")
    print("RESUME PARSED SUCCESSFULLY")
    print("==============================")