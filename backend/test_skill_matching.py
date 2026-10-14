
from tools import calculate_match

result = calculate_match(
    required_skills=[
        "React",
        "RESTful APIs",
        "SQL databases",
        "Programming Languages (Python, Java, C++, JavaScript)",
        "AWS",
    ],
    candidate_skills=[
        "React.js",
        "REST APIs",
        "PostgreSQL",
        "Python",
    ],
)

print("\nSKILL MATCH TEST")
print("Matched:", result["matched_skills"])
print("Missing:", result["missing_skills"])
print("Percentage:", result["match_percentage"])
