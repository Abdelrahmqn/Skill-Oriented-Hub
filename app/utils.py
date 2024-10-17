import os
from werkzeug.utils import secure_filename

def save_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join('static/uploads', filename)
    file.save(filepath)
    return filepath

def delete_file_if_exists(filepath):
    if filepath and os.path.exists(filepath):
        os.remove(filepath)

def get_embed_url(youtube_link):
    # Convert YouTube watch links or youtu.be links to embed links
    if "youtu.be" in youtube_link:
        video_id = youtube_link.split('/')[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "watch?v=" in youtube_link:
        video_id = youtube_link.split('watch?v=')[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    else:
        return youtube_link
