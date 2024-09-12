import streamlit as st
from dotenv import load_dotenv
load_dotenv() #load all the env variavles
import google.generativeai as genai
import os

from youtube_transcript_api import YouTubeTranscriptApi


genai.configure(api_key="AIzaSyAfdQk9QbT30BfNwHfDJGZaIBVqS-781J8")

prompt="""You are a Youtube Video Summarizer.You will be taking the transcript text and summarize the entire video and providing the important summary in points within 250 words.Please Provide the summary of the text given here:  """

from youtube_transcript_api import TranscriptsDisabled
## getting the transcript data from the youtube videos

def extract_transcript_details(youtube_video_url):
    try:
        video_id=youtube_video_url.split("=")[1]
        print(video_id)
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)
        transcript=""
        for i in transcript_text:
            transcript+=" "+i["text"]
        return transcript




    except Exception as e:
        raise e


## getting the summary based on Prompt from Gooogle Gemini Pro

def generate_gemini_content(transcript_text,prompt):

    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text



st.title("Youtube Transcript to Detailed Notes Converter")
youtube_link=st.text_input("Enter the youtube video Link:")

if youtube_link:
    video_id=youtube_link.split("=")[1]
    print(video_id)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg",use_column_width=True)


if st.button("Get Detailed Notes"):
    transcript_text=extract_transcript_details(youtube_link)

    if transcript_text:
        summary=generate_gemini_content(transcript_text,prompt)
        st.markdown("## Detailed Notes")
        st.write(summary)


