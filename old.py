from flask import Flask, request, render_template, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

# Load API keys from environment variables
openai_api_key = 'sk-proj-JcfaXUWJErL8rBJzzH0xT3BlbkFJRXKtdKg473mjo6sIW2vV'
eleven_labs_api_key = 'be139e9eae02754205b8d93b2859e279'

if not openai_api_key or not eleven_labs_api_key:
    raise ValueError("API keys are not set in environment variables")

client = OpenAI(api_key=openai_api_key)

def generate_transcript(topic):
    prompt = f"Create a podcast transcript about {topic}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a podcast generator. You will be given a topic and you will generate a transcript for the podcast on the given topic. The podcast should be in a monologue format. In your response you should include only text that is meant to be spoken (i.e. no 'host' and no '[Theme Song'). "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )
    return response.choices[0].message.content



# def generate_transcript(topic):
#     prompt = f"Create a podcast transcript about {topic}."
    
#     # Ensure to replace 'your_assistant_id_here' with the actual assistant ID
#     response = client.assistants.messages.create(  
#         assistant_id="asst_fdf19kxSdhwKVpR5HO0Ojr1G",  # Use the correct assistant ID
#         input_message={
#             "role": "user",
#             "content": prompt
#         },
#         max_tokens=4000
#     )
    
#     # Extract and return the content from the response
#     return response['message']['content']




def text_to_speech(text, topic):
    CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
    VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # ID of the voice model to use
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

