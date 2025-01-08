from youtubesearchpython import VideosSearch

def search_youtube(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    if 'result' in result and len(result['result']) > 0:
        video_info = result['result'][0]
        return video_info.get('link', '')
    return None

print(search_youtube("What is Retrieval-Augmented Generation (RAG)?"))
