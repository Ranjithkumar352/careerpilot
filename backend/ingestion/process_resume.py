
from ingestion.pdf_parser import extract_text_from_pdf
from ingestion.resume_parser import parse_resume_sections

from chunker import chunk_resume
from vector_store import VectorStore, DEFAULT_STORE_PATH


def process_resume(pdf_path, store_path=None):
    """
    Process a resume PDF and save its embeddings.

    Pipeline:
        PDF -> Text extraction -> Section parsing
        -> Chunking -> Embeddings -> Vector storage

    If store_path is provided, use that dedicated index.
    Otherwise, preserve the existing default index behavior.
    """

    print("\n📄 Processing resume...")

    # 1. Extract PDF text
    text = extract_text_from_pdf(pdf_path)

    if not text or not text.strip():
        raise ValueError(
            "Could not extract text from the resume."
        )

    print("✅ Resume text extracted.")

    # 2. Parse resume sections
    sections = parse_resume_sections(text)

    if not sections:
        raise ValueError(
            "Could not identify any resume sections."
        )

    print(f"✅ Resume sections detected: {len(sections)}")

    # 3. Convert sections into chunks
    chunks = []

    for section_name, content in sections.items():
        if not content or not content.strip():
            continue

        section_chunks = chunk_resume(
            f"{section_name.upper()}:\n{content}"
        )

        chunks.extend(section_chunks)

    if not chunks:
        raise ValueError(
            "No searchable content could be created from the resume."
        )

    print(f"✅ Resume chunks created: {len(chunks)}")

    # 4. Generate embeddings and save to the selected index
    selected_store_path = (
        store_path
        if store_path is not None
        else DEFAULT_STORE_PATH
    )

    vector_store = VectorStore(
        store_path=selected_store_path
    )

    print("\n🧠 Generating embeddings...")

    vector_store.add_documents(chunks)

    print("✅ Resume embeddings generated.")

    vector_store.save()

    print("✅ Resume knowledge base saved.")

    # 5. Return ingestion result
    return {
        "status": "success",
        "message": "Resume parsed successfully.",
        "sections": sections,
        "chunks": chunks,
        "store_path": selected_store_path,
    }


if __name__ == "__main__":
    result = process_resume("resume.pdf")

    print("\n==============================")
    print("RESUME INGESTION COMPLETE")
    print("==============================")

    print("\nMessage:")
    print(result["message"])

    print("\nSections:")
    for section in result["sections"]:
        print(f"  ✓ {section}")

    print("\nTotal chunks:")
    print(len(result["chunks"]))

    print("\nIndex path:")
    print(result["store_path"])

    print("\n==============================")
    print("🚀 Resume ready for AI analysis")
    print("==============================")
