import os
import imageio
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import moviepy.editor as mp
from django.http import JsonResponse

def extract_frames(request):
    try:
        filename = os.path.join(settings.MEDIA_ROOT, "1.mp4")

        # get video details
        video_clip = mp.VideoFileClip(filename)
        duration = int(video_clip.duration)
        fps = int(video_clip.fps)
        width = video_clip.size[0]
        height = video_clip.size[1]
        total_frames = int(video_clip.duration * video_clip.fps)
        video_clip.close()

        # extract frames using imageio
        framedir = os.path.join(settings.MEDIA_ROOT, "frames")
        os.makedirs(framedir, exist_ok=True)  # Ensure frames directory exists

        with imageio.get_reader(filename, 'ffmpeg') as video_reader:
            for i, frame in enumerate(video_reader):
                imageio.imwrite(os.path.join(framedir, f'frame{i:04d}.jpg'), frame)

        # get the list of frames
        frames = []
        fs = FileSystemStorage()
        total_size = 0
        for i, file_name in enumerate(os.listdir(framedir)):
            if file_name.endswith('.jpg'):
                file_path = os.path.join(framedir, file_name)
                file_size = os.path.getsize(file_path)
                frames.append((fs.url(os.path.join('frames', file_name)), i+1))
                total_size += file_size

        # calculate total size in MB or KB
        if total_size >= 1024 * 1024:
            total_size_in_mb = f"{total_size / (1024 * 1024):.2f} MB"
        else:
            total_size_in_mb = f"{total_size / 1024:.2f} KB"

        # pass the frames to the template
        context = {'frames': frames,
                   'total_size': total_size_in_mb,
                   'total_frames': total_frames,
                   'video_duration': duration,
                   'video_fps': fps,
                   'video_width': width,
                   'video_height': height
                   }

        return render(request, 'extract_frames.html', context)

    except Exception as e:
        # Log the exception for debugging
        logging.error(f"Error in extract_frames: {e}")
        return JsonResponse({'error': 'An error occurred during frame extraction.'})
