from tools import search_resume


query = "What authentication experience does the candidate have?"

results = search_resume(
    query=query,
    top_k=3
)

print("\n==============================")
print("RESUME SEARCH RESULTS")
print("==============================")

for index, result in enumerate(results, start=1):

    print(f"\nResult {index}")
    print("Section:", result["section"])
    print("Similarity:", result["similarity"])
    print("Text:")
    print(result["text"])