import os 
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
    )

def tavily_search(query):
    response = client.search(
        query = query,
        max_results = 5
    )

    results = []

    for item,record in enumerate(response["results"], 1):
        title = record.get("title", "Unknown Title")
        url = record.get("url", "Unknown URL")
        snippet = record.get("content", "").strip()

        #Keeping only the first 300 characters of the snippet for brevity
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

        results.append(f"{item}.  **{title}**\nURL: {url}\n {snippet}")

    return "\n\n".join(results)