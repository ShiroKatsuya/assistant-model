from langchain_community.document_loaders.youtube import TranscriptFormat,YoutubeLoader


loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=TKCMw0utiak",
    add_video_info=True,
    transcript_format=TranscriptFormat.CHUNKS,
    chunk_size_seconds=30,
    use_oauth=True, 
    allow_oauth_cache=True
)
print("\n\n".join(map(repr, loader.load())))