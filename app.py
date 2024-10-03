from flask import Flask, request, render_template, jsonify
from openai import OpenAI
import requests
import os
import time  # Import time for sleep function

app = Flask(__name__)

# Load API keys from environment variables
openai_api_key = 'sk-proj-JcfaXUWJErL8rBJzzH0xT3BlbkFJRXKtdKg473mjo6sIW2vV'
eleven_labs_api_key = 'be139e9eae02754205b8d93b2859e279'

if not openai_api_key or not eleven_labs_api_key:
    raise ValueError("API keys are not set in environment variables")

client = OpenAI(api_key=openai_api_key)

# Modified generate_transcript function using gen_response and run_assistant logic
def generate_transcript(topic):
    assistant_id = "asst_fdf19kxSdhwKVpR5HO0Ojr1G"

    # Create a thread
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": topic,
            }
        ]
    )
    thread_id = thread.id

    # Send a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=topic
    )

    # Run the assistant
    new_message = run_assistant(thread)
    return new_message

def run_assistant(thread):
    # Retrieve the assistant details
    assistant = client.beta.assistants.retrieve("asst_fdf19kxSdhwKVpR5HO0Ojr1G")

    # Start the assistant run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Check the status until the run is completed
    while run.status != "completed":
        time.sleep(0.5)  # Be nice to the API
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Assuming you want the last message
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value

    return new_message

def text_to_speech(text, topic):
    CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
    VOICE_ID = "sPzOOqSRgtzdT8DPbJYh"  # ID of the voice model to use
    OUTPUT_FOLDER = "static/podcasts"  # Folder to save the output audio file
    OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, f"{topic}.mp3")  # Path to save the output audio file

    # Ensure the output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    headers = {
        'Accept': 'application/json',
        "xi-api-key": eleven_labs_api_key,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
    }
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    if response.ok:
        with open(OUTPUT_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        return OUTPUT_PATH
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_podcast', methods=['POST'])
def generate_podcast():
    topic = request.json.get('topic')
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    transcript = generate_transcript(topic)
    audio_path = text_to_speech(transcript, topic)

    if audio_path:
        return jsonify({"audio_path": audio_path})
    else:
        return jsonify({"error": "Failed to generate podcast"}), 500

if __name__ == '__main__':
    app.run(debug=True)

