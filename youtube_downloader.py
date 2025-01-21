from pytubefix import YouTube
import sys


def download_youtube_audio(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    filename = f"{yt.title}.mp3"  # Use video title as filename
    return audio_stream.download(filename=filename)

download_youtube_audio("https://youtube.com/shorts/xhJT0KD1p1o?si=KmULEdNx4NBMQGTG")



