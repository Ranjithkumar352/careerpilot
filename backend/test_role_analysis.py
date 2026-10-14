from tools import analyze_role


roles = [
    "Full Stack Developer",
    "AI Engineer",
    "Data Scientist"
]


for role in roles:

    print("\n==============================")
    print(f"ROLE: {role}")
    print("==============================")

    result = analyze_role(role)

    print("\nTechnical Skills:")
    for skill in result["technical_skills"]:
        print(" -", skill)

    print("\nSoft Skills:")
    for skill in result["soft_skills"]:
        print(" -", skill)

    print("\nResponsibilities:")
    for responsibility in result["responsibilities"]:
        print(" -", responsibility)