from tools import (
    analyze_role,
    search_resume,
    analyze_candidate_skills
)


role = "AI Engineer"

print("\n==============================")
print("ROLE ANALYSIS")
print("==============================")

role_analysis = analyze_role(role)

print("\nRequired Skills:")

for skill in role_analysis["technical_skills"]:
    print(" -", skill)


print("\n==============================")
print("RESUME SEARCH")
print("==============================")

results = search_resume(
    query="AI engineering skills Python machine learning deep learning computer vision TensorFlow PyTorch MLOps",
    top_k=5
)

resume_evidence = "\n\n".join(
    result["text"]
    for result in results
)

print("\nResume Evidence:")
print(resume_evidence)


print("\n==============================")
print("CANDIDATE SKILL ANALYSIS")
print("==============================")

candidate_analysis = analyze_candidate_skills(
    role=role,
    role_skills=role_analysis["technical_skills"],
    resume_evidence=resume_evidence
)

print("\nCandidate Skills:")

for skill in candidate_analysis["candidate_skills"]:
    print(" -", skill)


print("\nSkill Evidence:")

for item in candidate_analysis["skill_evidence"]:
    print(
        f" - {item['skill']}: "
        f"{item['evidence']}"
    )