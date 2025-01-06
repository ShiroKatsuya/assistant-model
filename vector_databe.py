import chromadb
from pprint import pprint
import google.generativeai as genai
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer

client = chromadb.Client()

# collection = client.create_collection("all-my-documents")

model = genai.GenerativeModel('gemini-1.5-flash')

collection = client.create_collection(
      name="all-my-documents", 
      metadata={"hnsw:space": "cosine"} # l2 is the default
  ) 


def get_and_transform_page(url):
    """Cache transformed pages for identical URLs"""
    loader = AsyncChromiumLoader([url])
    html = loader.load()[0]

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        [html],
        tags_to_extract=["p", "iframe", "video"],  # Added video-related tags
        remove_unwanted_tags=["a"]
    )

    return docs_transformed[0]  # Added missing return statement


collection.add(
    documents=[
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=jNQXAC9IVRw", 
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    ],
    metadatas=[{"topic": "video"}, {"topic": "video"}, {"topic": "video"}],
    ids=["video1", "video2", "video3"],
)


results = collection.query(
    query_texts=["Please provide a summary of this YouTube video Me At The Zoo"],
    n_results=1,
)

print(results)

query_text = f"Please watch this YouTube video and provide a detailed summary: {results['documents'][0]}"
response = model.generate_content(query_text)
cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
pprint(cleaned_response)


