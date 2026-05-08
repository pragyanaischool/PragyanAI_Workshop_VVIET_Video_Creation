import streamlit as st
import os
import glob

# Handling MoviePy version differences (v1.x vs v2.x)
try:
    from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
except ImportError:
    from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
import yt_dlp

# --- UI Config ---
st.set_page_config(page_title="PragyanAI Video Creator", layout="wide")

# Initialize Session State for audio persistence
if 'audio_path' not in st.session_state:
    st.session_state['audio_path'] = None

# --- Functions ---

def cleanup_temp_files():
    """Removes temporary files created during processing."""
    files = glob.glob("temp_*") + ["output_video.mp4", "temp_audio_manual.mp3"]
    for f in files:
        try:
            os.remove(f)
        except:
            pass
    st.session_state['audio_path'] = None

def download_youtube_audio(url):
    """Downloads only audio from YouTube using reliable settings."""
    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.google.com/',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        return "temp_audio.mp3"
    except Exception as e:
        raise e

def create_video(image_files, duplicate_count, fps, audio_path):
    """Processes images and merges with audio using MoviePy 2.0+ syntax."""
    clips = []
    duration_per_image = duplicate_count / fps
    target_resolution = (1280, 720) 

    for idx, img_file in enumerate(image_files):
        temp_img_path = f"temp_img_{idx}.png"
        with open(temp_img_path, "wb") as f:
            f.write(img_file.getbuffer())
        
        # MoviePy 2.0+ uses .with_duration() and .resized()
        clip = ImageClip(temp_img_path).with_duration(duration_per_image)
        clip = clip.resized(target_resolution) 
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.with_fps(fps)
    
    audio_clip = AudioFileClip(audio_path)
    if audio_clip.duration > final_video.duration:
        audio_clip = audio_clip.with_duration(final_video.duration)

    final_clip = final_video.with_audio(audio_clip)
    
    output_filename = "output_video.mp4"
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac")
    
    return output_filename

# --- Streamlit Interface ---

# Display logo if it exists
if os.path.exists("PragyanAI_Transperent.png"):
    st.image("PragyanAI_Transperent.png", width=200)

st.title("PragyanAI - Multimedia Merger")
st.markdown("Upload multiple images, specify timing, and add audio from a file or YouTube.")

with st.sidebar:
    st.header("Video Settings")
    fps = st.slider("Frames Per Second (FPS)", 1, 60, 24)
    duplicates = st.number_input("Frames per Image", min_value=1, value=48, help="Number of frames each image stays on screen.")
    
    if st.button("Clear Cache & Temp Files"):
        cleanup_temp_files()
        st.success("Cleaned up!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Images")
    uploaded_images = st.file_uploader("Upload Image Sequence", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploaded_images:
        st.write(f"✅ {len(uploaded_images)} images uploaded.")
        st.info(f"Total Duration: {(len(uploaded_images) * duplicates) / fps:.2f} seconds")

with col2:
    st.subheader("2. Audio")
    audio_source = st.radio("Source", ["Upload File", "YouTube Link"])
    
    if audio_source == "Upload File":
        uploaded_audio = st.file_uploader("Upload Audio", type=["mp3", "wav"])
        if uploaded_audio:
            manual_path = "temp_audio_manual.mp3"
            with open(manual_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            st.session_state['audio_path'] = manual_path
            st.success("Audio File Ready")
    else:
        yt_url = st.text_input("YouTube URL")
        if yt_url:
            if st.button("Fetch YouTube Audio"):
                with st.spinner("Downloading audio..."):
                    try:
                        res_path = download_youtube_audio(yt_url)
                        st.session_state['audio_path'] = res_path
                        st.success("YouTube Audio Ready!")
                    except Exception as e:
                        st.error(f"Download Error: {e}")
                        st.info("💡 YouTube often blocks cloud servers. If this fails, download the MP3 locally and use 'Upload File'.")

# Check status of audio in memory
if st.session_state['audio_path']:
    st.write("🎵 **Audio Status:** Loaded and Ready")
else:
    st.write("🎵 **Audio Status:** Not Loaded")

# --- Final Step ---
st.divider()
if st.button("🚀 Create & Play Video", use_container_width=True):
    # CRITICAL FIX: Check session_state instead of local variable
    if uploaded_images and st.session_state['audio_path']:
        try:
            with st.spinner("Rendering video... This may take a minute."):
                video_file = create_video(uploaded_images, duplicates, fps, st.session_state['audio_path'])
                st.video(video_file)
                
                with open(video_file, "rb") as f:
                    st.download_button("📥 Download Result", f, file_name="my_video.mp4")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        if not uploaded_images:
            st.warning("Please upload at least one image.")
        if not st.session_state['audio_path']:
            st.warning("Please provide an audio source (Upload or Fetch YouTube).")
          
