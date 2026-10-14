
from tools import search_resume
from role_suggestions import suggest_roles


def prepare_resume_for_careerpilot(store_path=None):

    print("\n📄 Resume processing completed.")

    results = search_resume(
        query="candidate skills experience projects technologies",
        top_k=8,
        store_path=store_path
    )

    resume_evidence = "\n\n".join(
        item["text"]
        for item in results
        if item.get("text")
    )

    if not resume_evidence.strip():
        raise ValueError(
            "No resume evidence found. Please upload and process a resume first."
        )

    suggestions = suggest_roles(resume_evidence)

    return {
        "resume_evidence": resume_evidence,
        "suggested_roles": suggestions["suggested_roles"]
    }
