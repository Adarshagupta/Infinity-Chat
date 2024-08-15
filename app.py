from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from together import Together
import os
import json
from dotenv import load_dotenv
import html

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the API key from the environment variable
together_api_key = os.getenv('TOGETHER_API_KEY')
if not together_api_key:
    raise ValueError("No Together API key set for TOGETHER_API_KEY")

client = Together(api_key=together_api_key)


def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])


def simulate_fine_tuning(extracted_text):
    # In a real scenario, you would use this data to fine-tune a model
    # For now, we'll just store it and use it as context
    return json.dumps({"context": extracted_text})


def generate_integration_code(api_key):
    return f'''
<!-- AI Chatbot -->
<div id="ai-chatbot" style="position: fixed; bottom: 20px; right: 20px; width: 300px; height: 400px; background-color: #f1f1f1; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden;">
    <div style="background-color: #007bff; color: white; padding: 10px; font-weight: bold;">AI Chatbot</div>
    <div id="chat-messages" style="flex-grow: 1; overflow-y: auto; padding: 10px;"></div>
    <div style="padding: 10px; border-top: 1px solid #ddd;">
        <input type="text" id="user-input" placeholder="Type your message..." style="width: 80%; padding: 5px;">
        <button onclick="sendMessage()" style="width: 18%; padding: 5px;">Send</button>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script>
const chatWithAI = async (input) => {{
    try {{
        const response = await axios.post('https://chatcat-s1ny.onrender.com/chat', {{
            input: input,
            api_key: '{api_key}'
        }});
        return response.data.response;
    }} catch (error) {{
        console.error('Error:', error);
        return 'An error occurred while chatting with the AI.';
    }}
}};

function addMessage(sender, message) {{
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${{sender}}:</strong> ${{message}}`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}}

async function sendMessage() {{
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message) {{
        addMessage('You', message);
        userInput.value = '';
        const response = await chatWithAI(message);
        addMessage('AI', response);
    }}
}}

// Initialize chat
addMessage('AI', 'Hello! How can I assist you today?');
</script>
'''


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_url', methods=['POST'])
def process_url():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        extracted_text = extract_text_from_url(url)
        fine_tuned_data = simulate_fine_tuning(extracted_text)
        api_key = f"user_{os.urandom(16).hex()}"  # Generate a unique API key
        integration_code = generate_integration_code(api_key)

        # In a real scenario, you'd store the api_key and fine_tuned_data in a database

        return jsonify({
            "message": "Processing complete",
            "api_key": api_key,
            "integration_code": integration_code  # Note: removed html.escape()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')
    api_key = request.json.get('api_key')

    if not user_input or not api_key:
        return jsonify({"error": "Input and API key are required"}), 400

    try:
        # In a real scenario, you'd retrieve the fine-tuned data using the api_key
        # For now, we'll use a dummy context
        context = "This is a dummy context for the fine-tuned model."

        messages = [{
            "role":
            "system",
            "content":
            f"You are a chatbot trained on the following website content: {context}"
        }, {
            "role": "user",
            "content": user_input
        }]

        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"])

        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
