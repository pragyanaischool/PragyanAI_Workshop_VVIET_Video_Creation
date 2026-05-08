import streamlit as st
import os
import glob
try:
    from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
except ImportError:
    from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
import yt_dlp

# --- UI Config ---
st.set_page_config(page_title="Image to Video Pro", layout="wide")

# --- Functions ---

def cleanup_temp_files():
    """Removes temporary files created during processing."""
    files = glob.glob("temp_*") + ["output_video.mp4"]
    for f in files:
        try:
            os.remove(f)
        except:
            pass

def download_youtube_audio(url):
    """Downloads only audio from YouTube using reliable settings."""
    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        # Instead of fake PO tokens, use impersonation to look like a real browser
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
        # Important: Don't specify extractor_args with fake tokens unless you are using a provider plugin
    }

    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            print(f"Downloading audio from {url}...")
            ydl.download([url])
        return "temp_audio.mp3"
    except Exception as e:
        print(f"Audio download failed: {e}")
        return None
    
def create_video(image_files, duplicate_count, fps, audio_path):
    clips = []
    duration_per_image = duplicate_count / fps
    
    # Define your target resolution (Full HD: 1920x1080 or HD: 1280x720)
    target_resolution = (1280, 720) 

    for idx, img_file in enumerate(image_files):
        temp_img_path = f"temp_img_{idx}.png"
        with open(temp_img_path, "wb") as f:
            f.write(img_file.getbuffer())
        
        # Load and Resize image to fill the target resolution
        # .resized(target_resolution) ensures all frames match
        clip = ImageClip(temp_img_path).with_duration(duration_per_image)
        clip = clip.resized(target_resolution) 
        
        clips.append(clip)
    
    # Combine clips
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.with_fps(fps)
    
    # Process Audio
    audio_clip = AudioFileClip(audio_path)
    if audio_clip.duration > final_video.duration:
        audio_clip = audio_clip.with_duration(final_video.duration)

    final_clip = final_video.with_audio(audio_clip)
    
    output_filename = "output_video.mp4"
    # Note: 'libx264' is standard for web playback
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac")
    
    return output_filename

# --- Streamlit Interface ---
st.image("PragyanAI_Transperent.png")
st.title("PragyanAI - Multimedia Merger")
st.markdown("Upload multiple images, specify timing, and add audio from a file or YouTube.")

with st.sidebar:
    st.header(" Video - Settings")
    fps = st.slider("Frames Per Second (FPS)", 1, 60, 24)
    duplicates = st.number_input("Frames per Image", min_value=1, value=48, help="How many frames each image stays on screen.")
    
    if st.button("Clear Temp Files"):
        cleanup_temp_files()
        st.success("Cleaned up!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Images")
    uploaded_images = st.file_uploader("Upload Image Sequence", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploaded_images:
        st.write(f"✅ {len(uploaded_images)} images uploaded.")
        st.info(f"Each image will play for {duplicates/fps:.2f} seconds.")

with col2:
    st.subheader("2. Audio")
    audio_source = st.radio("Source", ["Upload File", "YouTube Link"])
    
    audio_path = None
    if audio_source == "Upload File":
        uploaded_audio = st.file_uploader("Upload Audio", type=["mp3", "wav"])
        if uploaded_audio:
            audio_path = "temp_audio_manual.mp3"
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
    else:
        yt_url = st.text_input("YouTube URL")
        if yt_url:
            if st.button("Fetch YouTube Audio"):
                with st.spinner("Downloading..."):
                    try:
                        audio_path = download_youtube_audio(yt_url)
                        st.success("Audio Ready!")
                        st.session_state['yt_audio'] = audio_path
                    except Exception as e:
                        st.error("YouTube blocked the download (403 Forbidden).")
                        st.info("💡 **Workshop Workaround:** Cloud servers are often blocked by YouTube. Please use the 'Upload File' option and upload an MP3 file directly.")
# Persistence for YouTube audio
if 'yt_audio' in st.session_state and audio_source == "YouTube Link":
    audio_path = st.session_state['yt_audio']

# --- Final Step ---
st.divider()
if st.button(" Create & Play Video", use_container_width=True):
    if uploaded_images and audio_path:
        try:
            with st.spinner("Rendering video... This may take a minute."):
                video_file = create_video(uploaded_images, duplicates, fps, audio_path)
                st.video(video_file)
                
                with open(video_file, "rb") as f:
                    st.download_button("📥 Download Result", f, file_name="my_video.mp4")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload images and provide audio first.")

        
