from rag_agent import rag_agent


query = "How should plastic waste be recycled?"

results = rag_agent.search(query)


print("\nECO NEXUS RAG AGENT")
print("=" * 50)

print("Query:", query)

for i, result in enumerate(results, start=1):

    print(f"\nResult {i}")
    print("Source:", result["source"])
    print("Knowledge:", result["content"])