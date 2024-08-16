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
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2000 per day", "1000 per hour"]
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



def generate_integration_code(api_key):
    return f'''
<!-- AI Chatbot Integration -->
<script src="https://chatcat-s1ny.onrender.com/chatbot.js?api_key={api_key}"></script>
'''
@app.route('/chatbot.js', methods=['GET', 'POST'])
def chatbot_script():
    try:
        api_key = request.args.get('api_key')
        if not api_key:
            app.logger.error("API key not provided in request")
            return jsonify({"error": "API key is required"}), 400
        script = f'''
    (function() {{
        function loadChatbot() {{
            var chatbotDiv = document.createElement('div');
            chatbotDiv.id = 'ai-chatbot';
            chatbotDiv.innerHTML = `
                <div id="chat-header" class="chatbot-header">
                    <span>AI Chatbot</span>
                    <svg id="chatbot-toggle" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </div>
                <div id="chatbot-content" class="chatbot-content">
                    <div id="chat-messages" class="chat-messages"></div>
                    <div id="chat-input" class="chat-input">
                        <input type="text" id="user-input" placeholder="Type your message...">
                        <button onclick="sendMessage()">Send</button>
                    </div>
<p style="text-align: center; font-size: 0.7em; color: #888;">powered by ChatCat</p>                </div>
            `;
            document.body.appendChild(chatbotDiv);
            
            var style = document.createElement('style');
            style.textContent = `
                #ai-chatbot {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 350px;
                    background: rgba(255, 255, 255, 0.25);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    border-radius: 15px 15px 0 0;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    transition: all 0.3s ease;
                    font-family: Arial, sans-serif;
                }}
                #ai-chatbot:hover {{
                    transform: scale(1.02);
                }}
                .chatbot-header {{
                    background-color: #1a202c;
                    color: white;
                    padding: 16px;
                    font-weight: 600;
                    font-size: 18px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    cursor: pointer;
                }}
                #chatbot-toggle {{
                    transition: transform 0.3s ease;
                }}
                .chatbot-content {{
                    height: 450px;
                    display: flex;
                    flex-direction: column;
                }}
                .chat-messages {{
                    flex-grow: 1;
                    overflow-y: auto;
                    padding: 24px;
                }}
                .chat-messages::-webkit-scrollbar {{
                    width: 8px;
                }}
                .chat-messages::-webkit-scrollbar-track {{
                    background: #EDF2F7;
                }}
                .chat-messages::-webkit-scrollbar-thumb {{
                    background-color: #CBD5E0;
                    border-radius: 20px;
                    border: 3px solid #EDF2F7;
                }}
                .chat-input {{
                    padding: 16px;
                    border-top: 1px solid #E2E8F0;
                    display: flex;
                }}
                #user-input {{
                    flex-grow: 1;
                    padding: 8px 16px;
                    border: 1px solid #E2E8F0;
                    border-radius: 9999px;
                    margin-right: 8px;
                    font-size: 14px;
                }}
                #user-input:focus {{
                    outline: none;
                    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
                }}
                .chat-input button {{
                    background-color: #1a202c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 9999px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }}
                .chat-input button:hover {{
                    background-color: #2d3748;
                }}
                .message {{
                    margin-bottom: 12px;
                }}
                .message p {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 18px;
                    max-width: 80%;
                }}
                .ai-message p {{
                    background-color: #F3F4F6;
                }}
                .user-message {{
                    text-align: right;
                }}
                .user-message p {{
                    background-color: #EBF8FF;
                }}
            `;
            document.head.appendChild(style);
            
            window.chatWithAI = async function(input) {{
                try {{
                    const response = await fetch('https://chatcat-s1ny.onrender.com/chat', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            input: input,
                            api_key: '{api_key}'
                        }})
                    }});
                    const data = await response.json();
                    return data.response;
                }} catch (error) {{
                    console.error('Error:', error);
                    return `Error: ${{error.message || 'Unknown error occurred'}}`;
                }}
            }};

            window.addMessage = function(sender, message) {{
                const chatMessages = document.getElementById('chat-messages');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${{sender === 'You' ? 'user-message' : 'ai-message'}}`;
                messageElement.innerHTML = `<p>${{message}}</p>`;
                chatMessages.appendChild(messageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }};

            window.sendMessage = async function() {{
                const userInput = document.getElementById('user-input');
                const message = userInput.value.trim();
                if (message) {{
                    addMessage('You', message);
                    userInput.value = '';
                    const response = await chatWithAI(message);
                    addMessage('AI', response);
                }}
            }};

            // Add toggle functionality
            document.getElementById('chat-header').addEventListener('click', function() {{
                var content = document.getElementById('chatbot-content');
                var toggle = document.getElementById('chatbot-toggle');
                if (content.style.display === 'none') {{
                    content.style.display = 'flex';
                    toggle.style.transform = 'rotate(180deg)';
                }} else {{
                    content.style.display = 'none';
                    toggle.style.transform = 'rotate(0deg)';
                }}
            }});

            // Initialize chat
            addMessage('AI', 'Hello! How can I assist you today?');
        }}

        if (document.readyState === 'complete') {{
            loadChatbot();
        }} else {{
            window.addEventListener('load', loadChatbot);
        }}
    }})();
    '''

        app.logger.info(f"Successfully generated chatbot script for API key: {api_key}")
        return Response(script, mimetype='application/javascript')
    except Exception as e:
        app.logger.error(f"Error in chatbot_script route: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
@app.route('/test_db')
def test_db():
    try:
        db.session.query("1").from_statement(text("SELECT 1")).all()
        return "Database connection successful"
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return f"Database connection failed: {str(e)}"

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
        app.logger.info(f"Extracted text for API key {api_key}: {extracted_text[:100]}...")  # Log first 100 chars

        user = User.query.get(session['user_id'])
        api_keys = json.loads(user.api_keys)
        api_keys.append(api_key)
        user.api_keys = json.dumps(api_keys)
        db.session.commit()

        integration_code = generate_integration_code(api_key)

        return jsonify({
            "message": "Processing complete",
            "api_key": api_key,
            "integration_code": integration_code
        })
    except Exception as e:
        app.logger.error(f"Error in process_url: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    try:
        user_input = request.json.get('input')
        api_key = request.json.get('api_key')

        if not user_input or not api_key:
            return jsonify({"error": "Input and API key are required"}), 400

        context = extracted_texts.get(api_key, "No context available for this API key.")
        app.logger.info(f"Context for API key {api_key}: {context[:100]}...")  # Log first 100 chars

        messages = [{
            "role": "system",
            "content": f"""You are a helpful AI assistant trained on the following website content: {context}

Instructions for providing responses:
1. Start with a brief, direct answer to the user's question.
2. If applicable, provide 2-3 key points or examples to support your answer.
3. Use bullet points or numbered lists for clarity when appropriate.
4. If the question is unclear, politely ask for clarification.
5. Keep your total response under 150 words unless more detail is explicitly requested.
6. End with a follow-up question or suggestion if relevant."""
        }, {
            "role": "user",
            "content": user_input
        }]

        logger.info(f"Sending request to Together API with input: {user_input}")
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
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
        app.logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/user/api_keys', methods=['GET'])
def get_user_api_keys():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    api_keys = json.loads(user.api_keys)
    return jsonify({"api_keys": api_keys})

@app.route('/chatbot-design', methods=['GET'])
def chatbot_design():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    design = f'''
<div id="ai-chatbot" style="position: fixed; bottom: 20px; right: 20px; width: 300px; font-family: Arial, sans-serif; transition: all 0.3s ease-in-out; z-index: 1000;">
    <div id="chat-header" style="background-color: #007bff; color: white; padding: 10px; font-weight: bold; cursor: pointer; border-radius: 10px 10px 0 0; display: flex; justify-content: space-between; align-items: center;">
        <span>AI Chatbot</span>
        <span id="toggle-chat" style="font-size: 20px;">−</span>
    </div>
    <div id="chat-body" style="display: block; background-color: #f1f1f1; border-radius: 0 0 10px 10px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
        <div id="chat-messages" style="height: 300px; overflow-y: auto; padding: 10px;"></div>
        <div style="padding: 10px; border-top: 1px solid #ddd; display: flex;">
            <input type="text" id="user-input" placeholder="Type your message..." style="flex-grow: 1; padding: 5px; margin-right: 5px;">
            <button onclick="sendMessage()" style="padding: 5px 10px; background-color: #007bff; color: white; border: none; cursor: pointer;">Send</button>
        </div>
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
            if (error.response) {{
                return `Server Error: ${{error.response.data.error || 'Unknown server error'}}`;
            }} else if (error.request) {{
                return 'Network Error: No response received from the server. Please check your internet connection.';
            }} else {{
                return `Error: ${{error.message}}`;
            }}
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

    // Toggle chat visibility
    document.getElementById('chat-header').addEventListener('click', function() {{
        const chatBody = document.getElementById('chat-body');
        const toggleChat = document.getElementById('toggle-chat');
        if (chatBody.style.display === 'none') {{
            chatBody.style.display = 'block';
            toggleChat.textContent = '−';
        }} else {{
            chatBody.style.display = 'none';
            toggleChat.textContent = '+';
        }}
    }});

    // Initialize chat
    addMessage('AI', 'Hello! How can I assist you today?');
</script>
'''

@app.route('/delete_api_key', methods=['POST'])
def delete_api_key():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    api_key = request.json.get('api_key')
    if not api_key:
        return jsonify({"error": "No API key provided"}), 400

    user = User.query.get(session['user_id'])
    api_keys = json.loads(user.api_keys)
    
    if api_key in api_keys:
        api_keys.remove(api_key)
        user.api_keys = json.dumps(api_keys)
        db.session.commit()
        
        # Also remove the extracted text for this API key
        extracted_texts.pop(api_key, None)
        
        return jsonify({"message": "API key deleted successfully"}), 200
    else:
        return jsonify({"error": "API key not found"}), 404
    
    return Response(design, mimetype='text/html')

@app.route('/test_together_api')
def test_together_api():
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return "Together API connection successful"
    except Exception as e:
        app.logger.error(f"Together API connection error: {str(e)}")
        return f"Together API connection failed: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
