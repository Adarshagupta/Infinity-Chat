from flask import Flask, request, jsonify, render_template, session, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup
from together import Together
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import uuid
import re

# Load environment variables from .env file
load_dotenv()

# Get the API keys from the environment variables
together_api_key = os.getenv('TOGETHER_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not together_api_key:
    raise ValueError("No Together API key set for TOGETHER_API_KEY")
if not openai_api_key:
    raise ValueError("No OpenAI API key set for OPENAI_API_KEY")

together_client = Together(api_key=together_api_key)
openai_client = OpenAI(api_key=openai_api_key)

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

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_keys = db.relationship('APIKey', backref='user', lazy=True)

# APIKey model
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    llm = db.Column(db.String(50), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
                        <button id="send-button">Send</button>
                    </div>
                   <p style="text-align: center; font-size: 0.7em; color: #888;">powered by <a href="#">NeuroWeb</a></p>               
                </div>
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
                .product-card {{
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px;
                    margin-top: 8px;
                    background-color: #f8fafc;
                }}
                .product-image {{
                    width: 100%;
                    max-height: 150px;
                    object-fit: cover;
                    border-radius: 4px;
                    margin-bottom: 8px;
                }}
                .product-card h3 {{
                    font-size: 16px;
                    margin: 0 0 4px 0;
                }}
                .product-card .price {{
                    font-weight: bold;
                    color: #2d3748;
                    margin: 0 0 4px 0;
                }}
                .product-card .description {{
                    font-size: 14px;
                    color: #4a5568;
                    margin: 0 0 8px 0;
                }}
                .shop-button {{
                    display: inline-block;
                    background-color: #4299e1;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-size: 14px;
                    transition: background-color 0.3s ease;
                }}
                .shop-button:hover {{
                    background-color: #3182ce;
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
                    return data;
                }} catch (error) {{
                    console.error('Error:', error);
                    return {{error: `Error: ${{error.message || 'Unknown error occurred'}}`}};
                }}
            }};

            window.addMessage = function(sender, message) {{
                const chatMessages = document.getElementById('chat-messages');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${{sender === 'You' ? 'user-message' : 'ai-message'}}`;
                
                if (typeof message === 'object') {{
                    if (message.product_data) {{
                        const productData = message.product_data;
                        messageElement.innerHTML = `
                            <p>${{message.response}}</p>
                            <div class="product-card">
                                <img src="${{productData.image_url}}" alt="${{productData.name}}" class="product-image">
                                <h3>${{productData.name}}</h3>
                                <p class="price">${{productData.price}}</p>
                                <p class="description">${{productData.description}}</p>
                                <a href="${{productData.product_url}}" class="shop-button" target="_blank">Shop Now</a>
                            </div>
                        `;
                    }} else if (message.response) {{
                        messageElement.innerHTML = `<p>${{message.response}}</p>`;
                    }} else if (message.error) {{
                        messageElement.innerHTML = `<p class="error">${{message.error}}</p>`;
                    }} else {{
                        messageElement.innerHTML = `<p>Unexpected response format</p>`;
                    }}
                }} else {{
                    messageElement.innerHTML = `<p>${{message}}</p>`;
                }}
                
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

            // Add event listener for the send button
            document.getElementById('send-button').addEventListener('click', sendMessage);

            // Add event listener for the Enter key in the input field
            document.getElementById('user-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    sendMessage();
                }}
            }});

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
def home():
    return render_template('home.html')

@app.route('/api')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/project')
def projects():
    return render_template('products.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
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
    llm = request.json.get('llm')
    if not url or not llm:
        return jsonify({"error": "URL and LLM choice are required"}), 400

    try:
        extracted_text = extract_text_from_url(url)
        api_key = f"user_{uuid.uuid4().hex}"
        
        new_api_key = APIKey(
            key=api_key,
            llm=llm,
            extracted_text=extracted_text,
            user_id=session['user_id']
        )
        db.session.add(new_api_key)
        db.session.commit()

        integration_code = generate_integration_code(api_key)

        return jsonify({
            "message": "Processing complete",
            "api_key": api_key,
            "llm": llm,
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

        api_key_data = APIKey.query.filter_by(key=api_key).first()
        if not api_key_data:
            return jsonify({"error": "Invalid API key"}), 400

        context = api_key_data.extracted_text
        llm = api_key_data.llm

        messages = [{
            "role": "system",
            "content": f"""You are a highly specialized AI assistant trained on the following website content: {context}

Instruction set for responses:
1. Provide an immediate, concise answer to the user's query in 1-2 sentences.
2. If relevant, offer 2-3 key points or examples, using bullet points for clarity.
3. For complex queries, break down information into numbered steps or categories.
4. Actively seek clarification on ambiguous questions.
5. Strictly limit responses to 100 words unless explicitly asked for more detail.
6. End with a pointed follow-up question or actionable suggestion.

E-commerce specific instructions:
7. For product searches, extract and display:
   - Product name
   - Price
   - Brief description (max 15 words)
   - Thumbnail image URL
   - 'Shop Now' button with product URL
8. Compare similar products in a concise table format when applicable.
9. Highlight special offers, discounts, or limited-time deals.
10. Suggest complementary products or accessories.

Tone and style:
11. Maintain a professional yet conversational tone.
12. Use industry-specific terminology when appropriate.
13. Emphasize unique selling points and value propositions.
14. Anticipate and address common customer concerns or objections.

If more information is needed, prompt the user with 'Get more info?'"""
        }, {
            "role": "user",
            "content": user_input
        }]

        logger.info(f"Sending request to {llm.capitalize()} API with input: {user_input}")

        if llm == 'together':
            response = together_client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>", "<|eom_id|>"])
            ai_response = response.choices[0].message.content
        elif llm == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                frequency_penalty=0,
                presence_penalty=0)
            ai_response = response.choices[0].message.content
        else:
            return jsonify({"error": "Invalid LLM specified"}), 400

        logger.info(f"Received response from {llm.capitalize()} API: {ai_response}")

        # Process the AI response for e-commerce functionality
        processed_response = process_ecommerce_response(ai_response)

        return jsonify(processed_response)
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

def process_ecommerce_response(response):
    product_info = re.search(r'Product: (.*?)\nPrice: (.*?)\nDescription: (.*?)\nImage: (.*?)\nURL: (.*?)(\n|$)', response)
    
    if product_info:
        product_data = {
            "name": product_info.group(1),
            "price": product_info.group(2),
            "description": product_info.group(3),
            "image_url": product_info.group(4),
            "product_url": product_info.group(5)
        }
        
        return {
            "response": response,
            "product_data": product_data
        }
    else:
        return {"response": response}

@app.route('/user/api_keys', methods=['GET'])
def get_user_api_keys():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    api_keys = [{"api_key": key.key, "llm": key.llm} for key in user.api_keys]
    return jsonify({"api_keys": api_keys})

@app.route('/delete_api_key', methods=['POST'])
def delete_api_key():
    if 'user_id' not in session:
        app.logger.error("User not logged in")
        return jsonify({"error": "User not logged in"}), 401

    api_key_to_delete = request.json.get('api_key')
    if not api_key_to_delete:
        app.logger.error("No API key provided")
        return jsonify({"error": "No API key provided"}), 400

    api_key = APIKey.query.filter_by(key=api_key_to_delete, user_id=session['user_id']).first()
    if api_key:
        db.session.delete(api_key)
        db.session.commit()
        app.logger.info(f"API key deleted: {api_key_to_delete}")
        return jsonify({"message": "API key deleted successfully"}), 200
    else:
        app.logger.error(f"API key not found: {api_key_to_delete}")
        return jsonify({"error": "API key not found"}), 404

@app.route('/test_apis')
def test_apis():
    together_result = "Failed"
    openai_result = "Failed"

    try:
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        together_result = "Success"
    except Exception as e:
        logger.error(f"Together API connection error: {str(e)}")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        openai_result = "Success"
    except Exception as e:
        logger.error(f"OpenAI API connection error: {str(e)}")

    return f"Together API: {together_result}, OpenAI API: {openai_result}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5410)