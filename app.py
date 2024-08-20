from flask import Flask, request, jsonify, render_template, session, Response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
from datetime import datetime
import time
from alembic import op
import sqlalchemy as sa


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
migrate = Migrate(app, db)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_keys = db.relationship('APIKey', backref='user', lazy=True)
    custom_prompts = db.relationship('CustomPrompt', backref='user', lazy=True)

# APIKey model
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    llm = db.Column(db.String(50), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# CustomPrompt model
class CustomPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt = db.Column(db.String(255), nullable=False)
    response = db.Column(db.Text, nullable=False)

# Add this after the CustomPrompt model
class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    endpoint = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float, nullable=False)
    status_code = db.Column(db.Integer, nullable=False)



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

        # Read the script from design.txt
        script_path = os.path.join(app.root_path, 'design.txt')
        with open(script_path, 'r') as file:
            script = file.read()

        # Replace placeholders with actual API key
        script = script.replace('{api_key}', api_key)

        return Response(script, mimetype='application/javascript')
    except Exception as e:
        app.logger.error(f"Error in chatbot_script: {str(e)}")
        return jsonify({"error": "An error occurred while generating the chatbot script"}), 500

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

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

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
    start_time = time.time()
    try:
        user_input = request.json.get('input')
        api_key = request.json.get('api_key')

        if not user_input or not api_key:
            return jsonify({"error": "Input and API key are required"}), 400

        api_key_data = APIKey.query.filter_by(key=api_key).first()
        if not api_key_data:
            return jsonify({"error": "Invalid API key"}), 400

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
                max_tokens=100,
                temperature=2,
                top_p=1,
                top_k=100,
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

        # Record analytics
        # Record analytics
        end_time = time.time()
        response_time = end_time - start_time
        analytics = Analytics(
            user_id=api_key_data.user_id,
            api_key=api_key,
            endpoint='/chat',
            response_time=response_time,
            status_code=200
        )
        db.session.add(analytics)
        db.session.commit()
        app.logger.info(f"Recorded analytics for user_id: {api_key_data.user_id}, api_key: {api_key}")

        return jsonify(processed_response)
    except Exception as e:
        app.logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        
        # Record analytics for error case
        end_time = time.time()
        response_time = end_time - start_time
        analytics = Analytics(
            user_id=api_key_data.user_id if 'api_key_data' in locals() else None,
            api_key=api_key if 'api_key' in locals() else None,
            endpoint='/chat',
            response_time=response_time,
            status_code=500
        )
        db.session.add(analytics)
        db.session.commit()
        app.logger.info(f"Recorded error analytics for api_key: {api_key}")
        
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

# Add this new route to retrieve analytics data
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    app.logger.info("Accessing /api/analytics route")
    
    try:
        if 'user_id' not in session:
            app.logger.warning("User not logged in")
            return jsonify({"error": "User not logged in"}), 401

        user_id = session['user_id']
        app.logger.info(f"Fetching analytics for user_id: {user_id}")
        
        analytics = Analytics.query.filter_by(user_id=user_id).all()
        app.logger.info(f"Found {len(analytics)} analytics entries")
        
        analytics_data = [{
            'api_key': a.api_key,
            'endpoint': a.endpoint,
            'timestamp': a.timestamp.isoformat(),
            'response_time': a.response_time,
            'status_code': a.status_code
        } for a in analytics]

        return jsonify(analytics_data)
    except Exception as e:
        app.logger.error(f"Error in get_analytics: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/test/insert_analytics', methods=['GET'])
def test_insert_analytics():
    try:
        test_analytics = Analytics(
            user_id=1,  # Replace with a valid user_id
            api_key='test_key',
            endpoint='/test',
            response_time=0.5,
            status_code=200
        )
        db.session.add(test_analytics)
        db.session.commit()
        return jsonify({"message": "Test analytics data inserted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error in test_insert_analytics: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while inserting test data"}), 500

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


@app.route('/api/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    api_keys = user.api_keys
    custom_prompts = user.custom_prompts

    # Fetch analytics data
    analytics = Analytics.query.filter_by(user_id=user.id).order_by(Analytics.timestamp.desc()).limit(100).all()
    
    analytics_data = [{
        'api_key': a.api_key,
        'endpoint': a.endpoint,
        'timestamp': a.timestamp.isoformat(),
        'response_time': a.response_time,
        'status_code': a.status_code
    } for a in analytics]

    return render_template('dashboard.html', user=user, api_keys=api_keys, custom_prompts=custom_prompts, analytics_data=analytics_data)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        new_email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_email:
            user.email = new_email

        if new_password and new_password == confirm_password:
            user.password = generate_password_hash(new_password)
        elif new_password and new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('profile'))

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/delete_api_key', methods=['POST'])
def delete_api_key():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    api_key_id = request.form.get('api_key_id')
    api_key = APIKey.query.get(api_key_id)
    if api_key and api_key.user_id == session['user_id']:
        db.session.delete(api_key)
        db.session.commit()
        flash('API key deleted successfully', 'success')
    else:
        flash('API key not found or you do not have permission to delete it', 'error')

    return redirect(url_for('dashboard'))

@app.route('/add_custom_prompt', methods=['POST'])
def add_custom_prompt():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    prompt = request.form.get('prompt')
    response = request.form.get('response')
    if prompt and response:
        new_prompt = CustomPrompt(user_id=session['user_id'], prompt=prompt, response=response)
        db.session.add(new_prompt)
        db.session.commit()
        flash('Custom prompt added successfully', 'success')
    else:
        flash('Prompt and response are required', 'error')

    return redirect(url_for('dashboard'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    user = User.query.get(session['user_id'])
    if user and check_password_hash(user.password, current_password):
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')
    else:
        flash('Current password is incorrect', 'error')

    return redirect(url_for('dashboard'))

@app.route('/test_api_key', methods=['POST'])
def test_api_key():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    api_key = request.json.get('api_key')
    test_input = request.json.get('input', "Hello, this is a test message.")

    api_key_data = APIKey.query.filter_by(key=api_key).first()
    if not api_key_data:
        return jsonify({"error": "Invalid API key"}), 400

    try:
        response = requests.post('http://localhost:5410/chat', json={
            'input': test_input,
            'api_key': api_key
        })
        
        return jsonify({
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.json()
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"API test failed: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5410)