import gradio as gr
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
import threading
from prometheus_client import start_http_server, Counter, Histogram
from transformers import pipeline


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


PROMPT = """You are a YouTube Video Summarizer. You will take the transcript text and summarize the entire video, providing the important summary in points within 250 words. Please provide the summary of the text given here: """


SUMMARIZATIONS_TOTAL = Counter('youtube_summarizations_total', 'Total number of YouTube transcript summarizations made')
SUMMARIZATION_ERRORS = Counter('youtube_summarization_errors_total', 'Total number of errors during summarization')
TRANSCRIPT_LENGTH = Histogram('youtube_transcript_length', 'Distribution of transcript lengths')
SUMMARY_LENGTH = Histogram('youtube_summary_length', 'Distribution of summary lengths')


def start_metrics_server():
    start_http_server(8000)


metrics_thread = threading.Thread(target=start_metrics_server, daemon=True)
metrics_thread.start()


def extract_video_id(youtube_url):
    youtube_regex = (r'(https?://)?(www\.)?'
                     r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
                     r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_match = re.match(youtube_regex, youtube_url)

    if youtube_match:
        return youtube_match.group(6)
    else:
        raise ValueError("Invalid YouTube URL")


def extract_transcript(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript_data])
        TRANSCRIPT_LENGTH.observe(len(transcript.split()))
        return transcript
    except Exception as e:
        SUMMARIZATION_ERRORS.inc()
        return f"Error extracting transcript: {str(e)}"


def split_text(text, max_words=1024):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks


def generate_summary(transcript_text):
    try:

        chunks = split_text(transcript_text, max_words=1024)
        summaries = []
        for chunk in chunks:
            full_text = chunk
            summary = summarizer(full_text, max_length=250, min_length=80, do_sample=False)
            summaries.append(summary[0]['summary_text'])

        combined_summary = ' '.join(summaries)

        final_summary = summarizer(combined_summary, max_length=250, min_length=80, do_sample=False)
        SUMMARIZATIONS_TOTAL.inc()
        SUMMARY_LENGTH.observe(len(final_summary[0]['summary_text'].split()))
        return final_summary[0]['summary_text']
    except Exception as e:
        SUMMARIZATION_ERRORS.inc()
        return f"Error generating summary: {str(e)}"


def summarize_youtube_video(youtube_url):
    transcript = extract_transcript(youtube_url)
    if transcript.startswith("Error"):
        return transcript
    summary = generate_summary(transcript)
    return summary


with gr.Blocks() as demo:
    gr.Markdown("# 📺 YouTube Transcript Summarizer")
    gr.Markdown("Convert YouTube video transcripts into concise summaries.")

    with gr.Tab("Summarize"):
        youtube_link = gr.Textbox(
            label="Enter YouTube Video Link:",
            placeholder="https://www.youtube.com/watch?v=XXXXXXXXXXX"
        )
        summarize_button = gr.Button("Summarize")
        summary_output = gr.Textbox(
            label="Summary",
            lines=15
        )

        summarize_button.click(
            fn=summarize_youtube_video,
            inputs=youtube_link,
            outputs=summary_output
        )

    with gr.Tab("About"):
        gr.Markdown("""
        ## About This App

        This application extracts transcripts from YouTube videos and summarizes them using Hugging Face's Transformers library.

        ### Features:
        - **Transcript Extraction**: Retrieves the transcript of any YouTube video (if available).
        - **Summarization**: Provides a concise summary of the video's content.

        ### Technologies Used:
        - [Gradio](https://gradio.app/) for the user interface.
        - [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for extracting transcripts.
        - [Hugging Face Transformers](https://huggingface.co/transformers/) for text summarization.
        - [Prometheus Client](https://github.com/prometheus/client_python) for metrics monitoring.

        ### Setup Instructions:
        1. Clone the repository.
        2. Install the required packages:
            ```bash
            pip install -r requirements.txt
            ```
        3. Run the application:
            ```bash
            python app.py
            ```
        4. Access the app at `http://localhost:7860` .
        """)

if __name__ == "__main__":
    demo.launch()
