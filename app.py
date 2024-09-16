import streamlit as st
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from huggingface_hub import InferenceClient  # Hugging Face Inference Client

# Load Hugging Face API key from environment variable
huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')

# Initialize the Hugging Face Inference Client (without api_token in constructor)
client = InferenceClient()

# Prompt for summarization
prompt = """You are a Youtube Video Summarizer. You will take the transcript text and summarize the entire video, providing the important summary in points within 250 words. Please provide the summary of the text given here: """

# Helper function to extract video ID from various YouTube URL formats
def extract_video_id(youtube_url):
    # Match for different YouTube URL structures
    youtube_regex = (r'(https?://)?(www\.)?'
                     '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                     '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_match = re.match(youtube_regex, youtube_url)
    
    if youtube_match:
        return youtube_match.group(6)
    else:
        raise ValueError("Invalid YouTube URL")

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        # Extract the video ID
        video_id = extract_video_id(youtube_video_url)
        print(video_id)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript

    except Exception as e:
        raise e

# Function to generate summary using Hugging Face API
def generate_huggingface_summary(transcript_text, prompt):
    # Combine prompt with transcript
    full_text = prompt + transcript_text
    # Call the Hugging Face summarization API, passing api_token in request
    response = client.summarization(full_text, api_token=huggingface_api_key)
    return response['summary_text']

# Streamlit interface
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter the YouTube video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    # Extract transcript from YouTube
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        # Generate summary using Hugging Face API
        summary = generate_huggingface_summary(transcript_text, prompt)
        st.markdown("## Detailed Notes")
        st.write(summary)