import sys
import asyncio
from pathlib import Path
# Add backend to python path
BACKEND_DIR = Path(r"c:\Users\sreek\Desktop\Voltstream\backend")
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
from app.services.rag_service import retrieve_document_context
async def main():
    query = "How does smart charging help reduce peak demand?"
    print(f"Query: {query}\n")
    
    result = await retrieve_document_context(query)
    if not result.get("ok"):
        print("Error/No results:", result.get("message"))
        return
        
    context = result.get("context", [])
    print(f"Retrieved {len(context)} chunks. Showing top 3:\n")
    for idx, item in enumerate(context[:3], start=1):
        print(f"--- Chunk {idx} (Source: {item['source']}, Page: {item['metadata'].get('page')}, Distance: {item['distance']:.4f}) ---")
        print(item['text'][:300] + "...")
        print()
if __name__ == "__main__":
    asyncio.run(main())
