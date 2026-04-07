import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from rag.embedder import get_embeddings
from rag.vectorstore import load_vectorstore
from agents.market_agent import MarketAgent

llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = get_embeddings()
vs = load_vectorstore("rag/faiss_index", embeddings)
agent = MarketAgent(llm=llm, vectorstore=vs)
result = agent.run({})

print("=== RAW ===")
for item in result["market"]["raw"]:
    print(f"[{item['category']}]")
    print(f"  출처: {item['source']} | URL: {item['url']}")
    print(f"  내용: {item['content'][:200]}...")

print()
print("=== SUMMARY ===")
print(result["market"]["summary"])
