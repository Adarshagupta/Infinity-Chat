from flask import Flask, request, jsonify, render_template, session, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup
from together import Together
import os
import json
from dotenv import load_dotenv
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import uuid

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Configure SQLAlchemy
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
db = SQLAlchemy(app)

# Get the API key from the environment variable
together_api_key = os.getenv('TOGETHER_API_KEY')
if not together_api_key:
    raise ValueError("No Together API key set for TOGETHER_API_KEY")

client = Together(api_key=together_api_key)

# Store extracted text for each API key
extracted_texts = {}

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_keys = db.Column(db.Text)  # Store as JSON string

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, api_keys='[]')
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({"message": "Logged in successfully"}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/process_url', methods=['POST'])
@limiter.limit("5 per minute")
def process_url():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        extracted_text = extract_text_from_url(url)
        api_key = f"user_{uuid.uuid4().hex}"
        extracted_texts[api_key] = extracted_text

        user = User.query.get(session['user_id'])
        api_keys = json.loads(user.api_keys)
        api_keys.append(api_key)
        user.api_keys = json.dumps(api_keys)
        db.session.commit()

        integration_code = generate_integration_script(api_key)

        response_data = {
            "message": "Processing complete",
            "api_key": api_key,
            "integration_code": integration_code
        }
        logger.info(f"Sending response: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in process_url: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def generate_integration_script(api_key):
    return f'''
<script>
(function() {{
    var script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js';
    script.onload = function() {{
        var chatbotScript = document.createElement('script');
        chatbotScript.textContent = `
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('DOM fully loaded and parsed');
                axios.get('https://chatcat-s1ny.onrender.com/chatbot-design?api_key={api_key}')
                    .then(function(response) {{
                        var div = document.createElement('div');
                        div.innerHTML = response.data;
                        document.body.appendChild(div);
                        
                        // Initialize chatbot functionality
                        const apiKey = '{api_key}';
                        console.log('API Key:', apiKey);

                        const chatWithAI = async (input) => {{
                            console.log('Sending message to AI:', input);
                            try {{
                                const response = await axios.post('https://chatcat-s1ny.onrender.com/chat', {{
                                    input: input,
                                    api_key: apiKey
                                }});
                                console.log('Received response from AI:', response.data);
                                return response.data.response;
                            }} catch (error) {{
                                console.error('Error in chatWithAI:', error);
                                throw error;
                            }}
                        }};

                        function addMessage(sender, message) {{
                            console.log(`Adding message from ${{sender}}:`, message);
                            const chatMessages = document.getElementById('chat-messages');
                            if (chatMessages) {{
                                const messageElement = document.createElement('div');
                                messageElement.innerHTML = `<strong>${{sender}}:</strong> ${{message}}`;
                                chatMessages.appendChild(messageElement);
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            }} else {{
                                console.error('Chat messages container not found');
                            }}
                        }}

                        async function sendMessage() {{
                            console.log('sendMessage function called');
                            const userInput = document.getElementById('user-input');
                            if (!userInput) {{
                                console.error('User input element not found');
                                return;
                            }}
                            const message = userInput.value.trim();
                            if (message) {{
                                console.log('User sending message:', message);
                                addMessage('You', message);
                                userInput.value = '';
                                try {{
                                    const response = await chatWithAI(message);
                                    console.log('Received AI response:', response);
                                    addMessage('AI', response);
                                }} catch (error) {{
                                    console.error('Error in sendMessage:', error);
                                    addMessage('AI', 'Sorry, there was an error processing your request.');
                                }}
                            }}
                        }}

                        // Initialize chat
                        console.log('Initializing chat');
                        addMessage('AI', 'Hello! How can I assist you today?');

                        // Add event listener for Enter key
                        const userInputElement = document.getElementById('user-input');
                        if (userInputElement) {{
                            userInputElement.addEventListener('keypress', function(event) {{
                                if (event.key === 'Enter') {{
                                    sendMessage();
                                }}
                            }});
                        }} else {{
                            console.error('User input element not found');
                        }}

                        // Add event listener for send button
                        const sendButton = document.getElementById('send-button');
                        if (sendButton) {{
                            sendButton.addEventListener('click', sendMessage);
                            console.log('Send button event listener added');
                        }} else {{
                            console.error('Send button not found');
                        }}
                    }})
                    .catch(function(error) {{
                        console.error('Error loading chatbot:', error);
                    }});
            }});
        `;
        document.body.appendChild(chatbotScript);
    }};
    document.body.appendChild(script);
}})();
</script>
'''
    
    return Response(design, mimetype='text/html')

@app.route('/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    try:
        user_input = request.json.get('input')
        api_key = request.json.get('api_key')

        if not user_input or not api_key:
            return jsonify({"error": "Input and API key are required"}), 400

        context = extracted_texts.get(api_key, "No context available for this API key.")

        messages = [{
            "role": "system",
            "content": f"You are a chatbot trained on the following website content: {context}"
        }, {
            "role": "user",
            "content": user_input
        }]

        logger.info(f"Sending request to Together API with input: {user_input}")
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"])
        logger.info(f"Received response from Together API: {response}")

        return jsonify({"response": response.choices[0].message.content})
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in chat route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Network error: {str(e)}"}), 503
    except Together.APIError as e:
        logger.error(f"Together API error in chat route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Together API error: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in chat route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/user/api_keys', methods=['GET'])
def get_user_api_keys():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    api_keys = json.loads(user.api_keys)
    return jsonify({"api_keys": api_keys})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)