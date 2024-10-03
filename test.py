from openai import OpenAI
from typing_extensions import override
import time

# Make sure you keep your API key secure
openai_api_key = 'sk-proj-JcfaXUWJErL8rBJzzH0xT3BlbkFJRXKtdKg473mjo6sIW2vV'  # Replace with a secure method for loading your API key
client = OpenAI(api_key=openai_api_key)

def gen_response(topic):
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
    print(new_message)

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

# Example usage:
gen_response("Biography of Mary Shelley")
