from django.shortcuts import render
from django.http import FileResponse
from pytube import YouTube, Playlist
import os
import shutil
from http.client import IncompleteRead


def download_audio(link):
    video = YouTube(link)
    try:
        stream = video.streams.get_audio_only()
        filename = stream.default_filename
        filename = filename[:filename.rfind('.')] + '.mp3'
        stream.download(output_path='downloads', filename=filename)
        return filename
    except IncompleteRead:
        print(f'Could not download: {link}')


def download(request):
    if request.method == 'POST':
        link = request.POST['link']
        if '&list=' in link:
            playlist = Playlist(link)
            for link in playlist.video_urls:
                download_audio(link)
            shutil.make_archive('audio_files', 'zip', 'downloads')
            response = FileResponse(open('audio_files.zip', 'rb'), as_attachment=True)
            os.remove('audio_files.zip')
        elif '\n' in link:
            links = link.split('\n')
            for link in links:
                download_audio(link)
            shutil.make_archive('audio_files', 'zip', 'downloads')
            response = FileResponse(open('audio_files.zip', 'rb'), as_attachment=True)
            os.remove('audio_files.zip')
        else:
            filename = download_audio(link)
            if filename is not None:
                response = FileResponse(open(os.path.join('downloads', filename), 'rb'), as_attachment=True)
            else:
                return render(request, 'audio.html')
        shutil.rmtree('downloads')
        os.mkdir('downloads')
        return response
    return render(request, 'audio.html')
