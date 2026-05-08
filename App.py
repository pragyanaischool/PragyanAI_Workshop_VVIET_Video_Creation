import streamlit as st
import os
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import yt_dlp

# --- Utility Functions ---

def download_youtube_audio(url):
    """Downloads audio from a YouTube URL and returns the filename."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "temp_audio.mp3"

def create_video(image_file, duplicate_count, fps, audio_path):
    """Creates a video by repeating a single image and attaching audio."""
    # Save the uploaded image temporarily
    with open("temp_img.png", "wb") as f:
        f.write(image_file.getbuffer())
    
    # Calculate duration of one 'frame' based on FPS
    frame_duration = 1 / fps
    
    # Create a clip from the image
    clip = ImageClip("temp_img.png").set_duration(frame_duration * duplicate_count)
    clip = clip.set_fps(fps)
    
    # Attach audio
    audio = AudioFileClip(audio_path)
    
    # If video is shorter than audio, loop video or trim audio
    # Here we match the audio duration to the video duration
    final_clip = clip.set_audio(audio.set_duration(clip.duration))
    
    output_path = "output_video.mp4"
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

# --- Streamlit UI ---

st.title("🖼️ Image-to-Video with Audio Merger")

# 1. Image Upload & Settings
st.header("Step 1: Configure Visuals")
uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])
col1, col2 = st.columns(2)
with col1:
    fps = st.number_input("Specify FPS (Frames Per Second)", min_value=1, value=24)
with col2:
    duplicates = st.number_input("Number of times to duplicate image", min_value=1, value=100)

total_seconds = duplicates / fps
st.info(f"Total Video Duration: {total_seconds:.2f} seconds")

# 2. Audio Input
st.header("Step 2: Add Audio")
audio_option = st.radio("Choose Audio Source:", ("Upload File", "YouTube Link"))

audio_file_path = None

if audio_option == "Upload File":
    uploaded_audio = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a"])
    if uploaded_audio:
        with open("temp_audio_upload.mp3", "wb") as f:
            f.write(uploaded_audio.getbuffer())
        audio_file_path = "temp_audio_upload.mp3"

else:
    yt_url = st.text_input("Enter YouTube Video URL")
    if yt_url and st.button("Extract Audio from YouTube"):
        with st.spinner("Extracting audio..."):
            try:
                audio_file_path = download_youtube_audio(yt_url)
                st.success("Audio extracted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

# 3. Process and Play
st.header("Step 3: Generate Video")
if st.button("Generate and Merge Video"):
    if uploaded_image and audio_file_path:
        with st.spinner("Processing video..."):
            video_path = create_video(uploaded_image, duplicates, fps, audio_file_path)
            
            st.success("Video Created!")
            st.video(video_path)
            
            # Download button
            with open(video_path, "rb") as file:
                st.download_button("Download Video", file, "final_video.mp4", "video/mp4")
    else:
        st.warning("Please ensure both image and audio are provided.")
