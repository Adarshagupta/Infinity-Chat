from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    Response,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
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
from datetime import datetime, timedelta
import time
from alembic import op
import sqlalchemy as sa
from functools import wraps
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import shopify
import woocommerce
import sqlalchemy
from collections import defaultdict
from itsdangerous import URLSafeTimedSerializer
import httpx
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import models
from models import db, User, APIKey, CustomPrompt, Analytics, AIModel, ModelReview, FineTuneJob, ChatInteraction, Conversation, EcommerceIntegration, Team, TeamMember, WebsiteInfo, FAQ

# Load environment variables from .env file
load_dotenv()

# Get the API keys from the environment variables
together_api_key = os.getenv("TOGETHER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
HUME_API_KEY = os.getenv('HUME_API_KEY')
HUME_SECRET_KEY = os.getenv('HUME_SECRET_KEY')

if not together_api_key:
    raise ValueError("No Together API key set for TOGETHER_API_KEY")
if not openai_api_key:
    raise ValueError("No OpenAI API key set for OPENAI_API_KEY")

together_client = Together(api_key=together_api_key)
openai_client = OpenAI(api_key=openai_api_key, base_url="https://api.aimlapi.com")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Add this after creating the Flask app
app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2000 per day", "1000 per hour"],
)

# Configure SQLAlchemy
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "fallback_secret_key_for_development"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///users.db")
db.init_app(app)
migrate = Migrate(app, db)

# Define the login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth"))
        return f(*args, **kwargs)
    return decorated_function

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join([p.text for p in soup.find_all("p")])

def generate_integration_code(api_key):
    return f"""
<!-- AI Chatbot Integration -->
<script src="https://infin8t.tech/chatbot.js?api_key={api_key}"></script>
"""

@app.route("/chatbot.js", methods=["GET", "POST"])
def chatbot_script():
    try:
        api_key = request.args.get("api_key")
        if not api_key:
            app.logger.error("API key not provided in request")
            return jsonify({"error": "API key is required"}), 400

        # Read the script from design.txt
        script_path = os.path.join(app.root_path, "design.txt")
        with open(script_path, "r") as file:
            script = file.read()

        # Replace placeholders with actual API key
        script = script.replace("{api_key}", api_key)

        return Response(script, mimetype="application/javascript")
    except Exception as e:
        app.logger.error(f"Error in chatbot_script: {str(e)}")
        return (
            jsonify({"error": "An error occurred while generating the chatbot script"}),
            500,
        )

@app.route("/test_db")
def test_db():
    try:
        db.session.query(func.now()).scalar()
        return "Database connection successful"
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return f"Database connection failed: {str(e)}"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/documentation")
def docs():
    return render_template("documentation.html")

@app.route("/project")
def projects():
    return render_template("products.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/auth")
@app.route("/login")
def auth():
    app.logger.info("Auth route accessed")
    return render_template('auth.html')

# SMTP configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Store OTPs temporarily (in a real application, use a database)
otps = {}

def send_otp(email):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    otps[email] = otp

    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = email
    message["Subject"] = "Your OTP for Chatcat Registration"
    
    html_body = f"""
    <html>
        <body>
            <h2>Welcome to Chatcat!</h2>
            <p>Thank you for registering with us. To complete your registration, please use the following One-Time Password (OTP):</p>
            <h1 style="color: #4CAF50; font-size: 40px;">{otp}</h1>
            <p>This OTP is valid for 10 minutes. If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>The Cartonify Team</p>
            <hr>
            <footer style="font-size: 12px; color: #666;">
                <p>
                    <a href="https://chatcat.com/terms">Terms and Conditions</a> | 
                    <a href="https://chatcat.com/privacy">Privacy Policy</a> | 
                    <a href="https://chatcat.com/docs">Documentation</a>
                </p>
            </footer>
        </body>
    </html>
    """
    
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)

@app.route('/send-otp', methods=['POST'])
def send_otp_route():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        send_otp(email)
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error sending OTP: {str(e)}")
        return jsonify({"error": "Failed to send OTP"}), 500

@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    password = request.json.get("password")
    otp = request.json.get("otp")

    if not email or not password or not otp:
        return jsonify({"error": "Email, password, and OTP are required"}), 400

    if otps.get(email) != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Clear the OTP after successful registration
    del otps[email]

    return jsonify({"message": "Registration successful"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        return jsonify({"message": "Logged in successfully", "redirect": "/dashboard/home"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully", "redirect": "/auth"}), 200

@app.route("/dashboard/home/process_url", methods=["POST"])
@limiter.limit("50 per minute")
def process_url():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    url = request.json.get("url")
    llm = request.json.get("llm")
    if not url or not llm:
        return jsonify({"error": "URL and LLM choice are required"}), 400

    try:
        extracted_text = extract_text_from_url(url)
        api_key = f"user_{uuid.uuid4().hex}"

        new_api_key = APIKey(
            key=api_key,
            llm=llm,
            extracted_text=extracted_text,
            user_id=session["user_id"],
        )
        db.session.add(new_api_key)
        db.session.commit()

        integration_code = generate_integration_code(api_key)

        return jsonify(
            {
                "message": "Processing complete",
                "api_key": api_key,
                "llm": llm,
                "integration_code": integration_code,
            }
        )
    except Exception as e:
        app.logger.error(f"Error in process_url: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def process_ecommerce_response(response):
    # Try to extract product information using regex
    product_info = re.search(
        r"Product: (.*?)\nPrice: (.*?)\nDescription: (.*?)\nImage: (.*?)\nURL: (.*?)(\n|$)",
        response,
    )

    if product_info:
        # If product information is found, structure it
        product_data = {
            "name": product_info.group(1),
            "price": product_info.group(2),
            "description": product_info.group(3),
            "image_url": product_info.group(4),
            "product_url": product_info.group(5),
        }

        return {"response": response, "product_data": product_data}
    else:
        # If no product information is found, return the response as is
        return {"response": response}

def generate_suggested_queries(context, conversation_history, num_suggestions=3):
    # Combine the context and conversation history
    full_text = context + ' ' + ' '.join([msg['content'] for msg in conversation_history])
    
    # Create a list of potential queries (you can expand this list)
    potential_queries = [
        "What are the main features?",
        "How does pricing work?",
        "Is there a free trial available?",
        "What kind of support do you offer?",
        "How secure is the platform?",
        "Can you explain the refund policy?",
        "What integrations are supported?",
        "How do I get started?",
        "What makes your product unique?",
        "Are there any case studies or testimonials?",
        "What's the typical onboarding process?",
        "How often do you release updates?",
        "What's your uptime guarantee?",
        "Do you offer custom solutions?",
        "What industries do you primarily serve?",
    ]

    # Vectorize the text and potential queries
    vectorizer = TfidfVectorizer().fit(potential_queries + [full_text])
    text_vector = vectorizer.transform([full_text])
    query_vectors = vectorizer.transform(potential_queries)

    # Calculate similarity scores
    similarities = cosine_similarity(text_vector, query_vectors)

    # Get indices of top similar queries
    top_indices = similarities.argsort()[0][-num_suggestions:][::-1]

    # Return the top suggested queries
    return [potential_queries[i] for i in top_indices]

@app.route("/chat", methods=["POST", "OPTIONS"])
@limiter.limit("50 per minute")
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    start_time = time.time()
    try:
        user_input = request.json.get("input")
        api_key = request.json.get("api_key")

        if not user_input or not api_key:
            return jsonify({"error": "Input and API key are required"}), 400

        api_key_data = APIKey.query.filter_by(key=api_key).first()
        if not api_key_data:
            return jsonify({"error": "Invalid API key"}), 400

        # Fetch or create conversation
        conversation = Conversation.query.filter_by(user_id=api_key_data.user_id, api_key_id=api_key_data.id).order_by(Conversation.updated_at.desc()).first()
        
        if not conversation or (datetime.utcnow() - conversation.created_at) > timedelta(hours=24):
            conversation = Conversation(user_id=api_key_data.user_id, api_key_id=api_key_data.id, messages=[])
            db.session.add(conversation)

        # Append user input to conversation history
        conversation.messages.append({"role": "user", "content": user_input})

        # Fetch the extracted text associated with this API key
        context = api_key_data.extracted_text

        # Fetch custom prompts for the user
        custom_prompts = CustomPrompt.query.filter_by(user_id=api_key_data.user_id).all()

        # Check if the query is related to e-commerce
        ecommerce_query_types = ['order_status', 'product_info', 'processing_time']
        query_type = next((qt for qt in ecommerce_query_types if qt in user_input.lower()), None)

        if query_type:
            # Extract the query parameter (e.g., order number or product ID)
            query_param = re.search(r'\d+', user_input)
            if query_param:
                query_param = query_param.group()
                ecommerce_data = get_ecommerce_data(api_key_data.user_id, query_type, query_param)
                if ecommerce_data:
                    return jsonify({"response": ecommerce_data})

        # Prepare messages for AI, including conversation history and custom prompts
        messages = [
            {
                "role": "system",
                "content": f"""You are an AI assistant specialized for this website. Use the following content as your knowledge base: {context}

Key guidelines:
1. Provide concise, accurate answers based on the website's content.
2. Use a professional yet friendly tone aligned with the brand voice.
3. Highlight key products, services, and unique selling points.
4. Offer relevant recommendations and cross-sell when appropriate.
5. Address common customer queries and concerns proactively.
6. Use industry-specific terminology when suitable.
7. Limit responses to 50 words unless more detail is requested.
8. End with a relevant follow-up question or call-to-action.
9. Remember and refer to previous parts of the conversation when relevant.

For e-commerce queries:
- Handle order status inquiries by providing the current status of the order.
- Provide product information including name, price, and stock availability.
- Inform about current processing times for orders.
- If you can't find specific e-commerce information, apologize and offer to connect the user with customer support.

Custom prompts:
{' '.join([f'- {prompt.prompt}: {prompt.response}' for prompt in custom_prompts])}

If you need more information to answer accurately, ask the user a clarifying question.""",
            }
        ] + conversation.messages[-5:]  # Include last 5 messages for context

        logger.info(f"Sending request to AI service with input: {user_input}")

        ai_response = get_ai_response(api_key_data.llm, messages)

        # Generate suggested queries based on context and conversation
        suggested_queries = generate_suggested_queries(context, conversation.messages)

        # Add suggested queries to the response
        response_with_suggestions = {
            "response": ai_response,
            "suggested_queries": suggested_queries
        }

        # Append AI response to conversation history
        conversation.messages.append({"role": "assistant", "content": json.dumps(response_with_suggestions)})
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        # Record analytics
        analytics = Analytics(
            user_id=api_key_data.user_id,
            api_key=api_key,
            endpoint="/chat",
            response_time=time.time() - start_time,
            status_code=200,
        )
        db.session.add(analytics)
        db.session.commit()
        app.logger.info(f"Analytics recorded for user_id: {api_key_data.user_id}, api_key: {api_key}")

        return jsonify(response_with_suggestions)
    except Exception as e:
        app.logger.error(f"Error in chat route: {str(e)}", exc_info=True)

        # Record analytics for error case
        analytics = Analytics(
            user_id=api_key_data.user_id if "api_key_data" in locals() else None,
            api_key=api_key if "api_key" in locals() else None,
            endpoint="/chat",
            response_time=time.time() - start_time,
            status_code=500,
        )
        db.session.add(analytics)
        db.session.commit()

        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# Add this new function to delete old conversations
def delete_old_conversations():
    with app.app_context():
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        old_conversations = Conversation.query.filter(Conversation.updated_at < cutoff_time).all()
        for conversation in old_conversations:
            db.session.delete(conversation)
        db.session.commit()
        app.logger.info(f"Deleted {len(old_conversations)} old conversations")

# Add this to your main block

# New route for feedback
@app.route("/feedback", methods=["POST"])
def feedback():
    interaction_id = request.json.get("interaction_id")
    is_helpful = request.json.get("is_helpful")

    interaction = ChatInteraction.query.get(interaction_id)
    if interaction:
        interaction.feedback = is_helpful
        db.session.commit()
        return jsonify({"message": "Feedback recorded successfully"}), 200
    else:
        return jsonify({"error": "Interaction not found"}), 404

# New function for contextual learning
def train_contextual_model(user_id):
    interactions = ChatInteraction.query.filter_by(user_id=user_id, feedback=True).all()
    
    if len(interactions) < 10:  # Require at least 10 positive interactions for training
        return None

    inputs = [interaction.user_input for interaction in interactions]
    responses = [interaction.ai_response for interaction in interactions]

    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(inputs)
    y = np.array(responses)

    model = MultinomialNB()
    model.fit(X, y)

    return (vectorizer, model)




# Update the clear_chat_history route
@app.route("/clear_chat_history", methods=["POST"])
def clear_chat_history():
    api_key = request.json.get("api_key")
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    api_key_data = APIKey.query.filter_by(key=api_key).first()
    if not api_key_data:
        return jsonify({"error": "Invalid API key"}), 400

    session.pop(f"conversation_history_{api_key}", None)
    session.modified = True

    return jsonify({"message": "Chat history cleared successfully"}), 200


# The rest of your code remains the same


def get_ai_response(llm_type, messages):
    user_id = session.get("user_id")
    
    if user_id:
        contextual_model = train_contextual_model(user_id)
        if contextual_model:
            vectorizer, model = contextual_model
            user_input = messages[-1]["content"]
            X = vectorizer.transform([user_input])
            predicted_response = model.predict(X)[0]
            
            # Use the predicted response as additional context
            messages.append({"role": "system", "content": f"Consider this relevant information: {predicted_response}"})

    if llm_type == "together":
        response = together_client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=messages,
            max_tokens=100,
            temperature=2,
            top_p=1,
            top_k=100,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
        )
        raw_response = response.choices[0].message.content
    elif llm_type == "openai":
        response = openai_client.chat.completions.create(
            model="gpt-4", messages=messages, max_tokens=128, temperature=0.7
        )
        raw_response = response.choices[0].message.content
    else:
        raise ValueError("Invalid LLM specified")

    # Ensure raw_response is a string
    if not isinstance(raw_response, str):
        raw_response = str(raw_response)

    structured_response = process_raw_response(raw_response)
    return structured_response

def process_raw_response(raw_response):
    # Split the response into sentences
    sentences = re.split(r'(?<=[.!?])\s+', raw_response)
    
    # Initialize structured response
    structured_response = {
        "introduction": "",
        "steps": [],
        "conclusion": ""
    }

    # Process sentences
    for sentence in sentences:
        if sentence.startswith(("With", "Using")):
            structured_response["introduction"] = sentence
        elif re.match(r'^\d+\.', sentence):
            # This is a numbered step
            step = re.sub(r'^\d+\.\s*', '', sentence)
            structured_response["steps"].append(step)
        elif sentence.startswith(("Finally", "In conclusion")):
            structured_response["conclusion"] = sentence
        else:
            # If it doesn't fit elsewhere, add it to the last step
            if structured_response["steps"]:
                structured_response["steps"][-1] += " " + sentence
            else:
                structured_response["introduction"] += " " + sentence

    return structured_response




def process_ecommerce_response(response):
    if isinstance(response, dict):
        # This is our new structured response
        return response
    
    # If it's not a dict, assume it's a string (old format)
    # Try to extract product information using regex
    product_info = re.search(
        r"Product: (.*?)\nPrice: (.*?)\nDescription: (.*?)\nImage: (.*?)\nURL: (.*?)(\n|$)",
        response,
    )

    if product_info:
        # If product information is found, structure it
        product_data = {
            "name": product_info.group(1),
            "price": product_info.group(2),
            "description": product_info.group(3),
            "image_url": product_info.group(4),
            "product_url": product_info.group(5),
        }

        return {"response": response, "product_data": product_data}
    else:
        # If no product information is found, return the response as is
        return {"response": response}


@app.route("/dashboard/home/user/api_keys", methods=["GET"])
@login_required
def get_user_api_keys():
    user = User.query.get(session["user_id"])
    api_keys = [{"id": key.id, "key": key.key, "llm": key.llm} for key in user.api_keys]
    return jsonify({"api_keys": api_keys})


# Add this new route to retrieve analytics data
@app.route("/dashboard/home/api/analytics", methods=["GET"])
@login_required
def get_analytics():
    try:
        user_id = session["user_id"]
        app.logger.info(f"Fetching analytics for user_id: {user_id}")
        
        # Get all analytics data for the user
        analytics = Analytics.query.filter_by(user_id=user_id).order_by(Analytics.timestamp.desc()).all()
        
        app.logger.info(f"Found {len(analytics)} analytics entries for user_id: {user_id}")

        if not analytics:
            return jsonify({"message": "No analytics data available", "analytics": [], "graph_data": [], "total_calls": 0, "avg_response_time": 0}), 200

        # Prepare data for charts
        daily_usage = defaultdict(int)
        response_times = []
        
        for entry in analytics:
            date = entry.timestamp.date()
            daily_usage[date] += 1
            response_times.append(entry.response_time)
        
        graph_data = [
            {"date": date.isoformat(), "count": count}
            for date, count in sorted(daily_usage.items())
        ]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        analytics_data = [
            {
                "api_key": a.api_key,
                "endpoint": a.endpoint,
                "timestamp": a.timestamp.isoformat(),
                "response_time": a.response_time,
                "status_code": a.status_code,
            }
            for a in analytics[:100]  # Limit to last 100 entries for the table
        ]
        
        result = {
            "analytics": analytics_data,
            "graph_data": graph_data,
            "avg_response_time": avg_response_time,
            "total_calls": len(analytics)
        }
        
        app.logger.info(f"Returning analytics data: {result}")
        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error in get_analytics: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching analytics data"}), 500

@app.route("/test_apis")
def test_apis():
    together_result = "Failed"
    openai_result = "Failed"

    try:
        response = together_client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
        )
        together_result = "Success"
    except Exception as e:
        logger.error(f"Together API connection error: {str(e)}")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
        ) 
        openai_result = "Success"
    except Exception as e:
        logger.error(f"OpenAI API connection error: {str(e)}")

    return f"Together API: {together_result}, OpenAI API: {openai_result}"


@app.route("/dashboard/home/api/update_profile", methods=["POST"])
@login_required
def update_profile():
    user = User.query.get(session["user_id"])
    
    new_email = request.form.get("email")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            flash("Email already in use", "error")
        else:
            user.email = new_email
            flash("Email updated successfully", "success")

    if new_password:
        if new_password == confirm_password:
            user.password = generate_password_hash(new_password)
            flash("Password updated successfully", "success")
        else:
            flash("Passwords do not match", "error")

    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@app.route("/dashboard/<section>")
@login_required
def dashboard_section(section=None):
    user = User.query.get(session["user_id"])
    custom_prompts = CustomPrompt.query.filter_by(user_id=user.id).all()
    website_info = WebsiteInfo.query.filter_by(user_id=user.id).first()
    faq_items = FAQ.query.filter_by(user_id=user.id).order_by(FAQ.order).all()
    return render_template("dashboard.html", user=user, active_section=section or "home", custom_prompts=custom_prompts, website_info=website_info, faq_items=faq_items)

@app.route('/subscription')
def subscription_page():
    subscription_plans = {
        'basic': {'price': 99900, 'api_calls': 1000},
        'pro': {'price': 199900, 'api_calls': 5000},
        'enterprise': {'price': 499900, 'api_calls': 20000}
    }
    return render_template('subscription.html', subscription_plans=subscription_plans, user=current_user)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        new_email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_email:
            user.email = new_email

        if new_password and new_password == confirm_password:
            user.password = generate_password_hash(new_password)
        elif new_password and new_password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("profile"))

        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


@app.route("/dashboard/home/delete_api_key", methods=["POST"])
@login_required
def delete_api_key():
    api_key_id = request.json.get('api_key_id')
    if not api_key_id:
        return jsonify({"error": "API key ID is required"}), 400

    api_key = APIKey.query.get(api_key_id)
    if not api_key or api_key.user_id != session["user_id"]:
        return jsonify({"error": "Invalid API key or you don't have permission to delete it"}), 404

    try:
        db.session.delete(api_key)
        db.session.commit()
        return jsonify({"message": "API key and associated conversations deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting API key: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the API key"}), 500


@app.route("/add_custom_prompt", methods=["POST"])
@login_required
def add_custom_prompt():
    prompt = request.form.get("prompt")
    response = request.form.get("response")
    if prompt and response:
        new_prompt = CustomPrompt(
            user_id=session["user_id"], prompt=prompt, response=response
        )
        db.session.add(new_prompt)
        db.session.commit()
        flash("Custom prompt added successfully", "success")
    else:
        flash("Prompt and response are required", "error")

    return redirect(url_for("dashboard_section", section="custom-prompts"))


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    user = User.query.get(session["user_id"])
    if user and check_password_hash(user.password, current_password):
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully", "success")
    else:
        flash("Current password is incorrect", "error")

    return redirect(url_for("dashboard"))


@app.route("/test_api_key", methods=["POST"])
@login_required
def test_api_key():
    api_key = request.json.get("api_key")
    test_input = request.json.get("input", "Hello, this is a test message.")

    api_key_data = APIKey.query.filter_by(key=api_key).first()
    if not api_key_data:
        return jsonify({"error": "Invalid API key"}), 400

    try:
        response = requests.post(
            "https://infin8t.tech/chat",
            json={"input": test_input, "api_key": api_key},
            timeout=10,
        )  # Add a timeout

        response.raise_for_status()  # Raises an HTTPError for bad responses

        return (
            jsonify(
                {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response": response.json(),
                }
            ),
            200,
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API test failed: {str(e)}")
        return jsonify({"error": f"API test failed: {str(e)}"}), 500
    except ValueError as e:  # This will catch json decode errors
        app.logger.error(f"Error decoding JSON response: {str(e)}")
        return jsonify({"error": f"Error decoding response: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in API test: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# New routes
@app.route("/ai_models", methods=["GET"])
def get_ai_models():
    models = AIModel.query.all()
    return jsonify(
        [
            {
                "id": model.id,
                "name": model.name,
                "description": model.description,
                "provider": model.provider,
                "documentation_url": model.documentation_url,
                "average_rating": get_average_rating(model.id),
            }
            for model in models
        ]
    )


@app.route("/ai_models/<int:model_id>", methods=["GET"])
def get_ai_model(model_id):
    model = AIModel.query.get_or_404(model_id)
    reviews = ModelReview.query.filter_by(model_id=model_id).all()
    return jsonify(
        {
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "provider": model.provider,
            "documentation_url": model.documentation_url,
            "average_rating": get_average_rating(model.id),
            "reviews": [
                {
                    "user_id": review.user_id,
                    "rating": review.rating,
                    "review_text": review.review_text,
                    "created_at": review.created_at,
                }
                for review in reviews
            ],
        }
    )

@app.route('/resend-otp', methods=['POST'])
def resend_otp_route():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        send_otp(email)
        return jsonify({"message": "OTP resent successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error resending OTP: {str(e)}")
        return jsonify({"error": "Failed to resend OTP"}), 500

@app.route("/ai_models/<int:model_id>/review", methods=["POST"])
def add_model_review(model_id):
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    new_review = ModelReview(
        user_id=session["user_id"],
        model_id=model_id,
        rating=data["rating"],
        review_text=data.get("review_text", ""),
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review added successfully"}), 201


def get_average_rating(model_id):
    reviews = ModelReview.query.filter_by(model_id=model_id).all()
    if not reviews:
        return 0
    return sum(review.rating for review in reviews) / len(reviews)

@app.route('/slack/oauth_callback')
@login_required
def slack_oauth_callback():
    code = request.args.get('code')
    client_id = os.getenv('SLACK_CLIENT_ID')
    client_secret = os.getenv('SLACK_CLIENT_SECRET')
    redirect_uri = url_for('slack_oauth_callback', _external=True)

    # Exchange the code for an access token
    response = requests.post('https://slack.com/api/oauth.v2.access', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    })

    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        # Store the access_token securely for the current user
        current_user.slack_token = access_token
        db.session.commit()
        flash('Slack integration successful!', 'success')
    else:
        flash('Slack integration failed.', 'error')

    return redirect(url_for('dashboard'))


@app.route("/ai_marketplace")
def ai_marketplace():
    models = AIModel.query.all()
    return render_template("ai_marketplace.html", models=models)
    training_file = data.get('training_file')

    if not api_key_id or not training_file:
        return jsonify({'error': 'API key and training file are required'}), 400

    api_key = APIKey.query.get(api_key_id)
    if not api_key or api_key.user_id != session['user_id']:
        return jsonify({'error': 'Invalid API key'}), 400

    # Here you would typically upload the training file to your AI provider
    # and start the fine-tuning process. For this example, we'll just create a job.
    new_job = FineTuneJob(
        user_id=session['user_id'],
        api_key_id=api_key_id,
        training_file=training_file,
        status='pending'
    )
    db.session.add(new_job)
    db.session.commit()

    # In a real scenario, you would start an asynchronous task here to monitor the fine-tuning process
    # and update the job status accordingly.

    return jsonify({'message': 'Fine-tuning job started successfully', 'job_id': new_job.id}), 201

@app.route('/api/fine-tune/status', methods=['GET'])
@login_required
def get_fine_tune_status():
    jobs = FineTuneJob.query.filter_by(user_id=session['user_id']).order_by(FineTuneJob.created_at.desc()).all()
    return jsonify([{
        'id': job.id,
        'status': job.status,
        'created_at': job.created_at.isoformat(),
        'updated_at': job.updated_at.isoformat(),
        'api_key': job.api_key.key,
        'model_name': job.model_name
    } for job in jobs])

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    data = request.json
    user_message = data.get('message')
    
    # Here you would typically process the user_message and generate a response
    # For now, we'll just echo the message back
    ai_response = f"You said: {user_message}"
    
    return jsonify({'response': ai_response})

# Add this new route
@app.route('/api/setup_webhook', methods=['POST'])
@login_required
def setup_webhook():
    user_id = session['user_id']
    webhook_url = request.json.get('webhook_url')
    
    if not webhook_url:
        return jsonify({'error': 'Webhook URL is required'}), 400

    # In a real application, you would store this webhook URL in the database
    # associated with the user_id
    # For this example, we'll just return a success message
    return jsonify({'message': 'Webhook setup successfully', 'webhook_url': webhook_url}), 200

@app.route('/api/ecommerce/integrate', methods=['POST'])
@login_required
def integrate_ecommerce():
    platform = request.json.get('platform')
    api_key = request.json.get('api_key')
    store_url = request.json.get('store_url')
    
    if not all([platform, api_key, store_url]):
        return jsonify({'error': 'All fields are required'}), 400
    
    new_integration = EcommerceIntegration(
        user_id=session['user_id'],
        platform=platform,
        api_key=api_key,
        store_url=store_url
    )
    db.session.add(new_integration)
    db.session.commit()
    
    return jsonify({'message': f'{platform} integration successful'}), 201

@app.route('/api/ecommerce/integrations', methods=['GET'])
@login_required
def get_ecommerce_integrations():
    integrations = EcommerceIntegration.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': i.id,
        'platform': i.platform,
        'store_url': i.store_url,
        'created_at': i.created_at.isoformat()
    } for i in integrations])

@app.route('/api/ecommerce/integrations/<int:integration_id>', methods=['DELETE'])
@login_required
def delete_ecommerce_integration(integration_id):
    integration = EcommerceIntegration.query.get_or_404(integration_id)
    if integration.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(integration)
    db.session.commit()
    return jsonify({'message': 'Integration deleted successfully'}), 200

@app.route('/api/teams', methods=['GET'])
@login_required
def get_teams():
    user = User.query.get(session['user_id'])
    teams = [{'id': tm.team.id, 'name': tm.team.name, 'role': tm.role} for tm in user.team_memberships]
    return jsonify(teams)

@app.route('/api/teams', methods=['POST'])
@login_required
def create_team():
    name = request.json.get('name')
    if not name:
        return jsonify({'error': 'Team name is required'}), 400

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    team = Team(name=name)
    db.session.add(team)
    db.session.flush()

    team_member = TeamMember(team_id=team.id, user_id=user.id, role='admin')
    db.session.add(team_member)

    db.session.commit()

    return jsonify({'message': 'Team created successfully', 'team_id': team.id}), 201

@app.route('/api/teams/<int:team_id>/invite', methods=['POST'])
@login_required
def invite_team_member(team_id):
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    team = Team.query.get(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if TeamMember.query.filter_by(team_id=team_id, user_id=user.id).first():
        return jsonify({'error': 'User is already a member of this team'}), 400

    team_member = TeamMember(team=team, user=user)
    db.session.add(team_member)
    db.session.commit()

    # Here you would typically send an email invitation to the user
    # For now, we'll just return a success message
    return jsonify({'message': f'Invitation sent to {email}'}), 200

@app.route('/api/teams/<int:team_id>/members', methods=['GET'])
@login_required
def get_team_members(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404

    members = [{'id': tm.user.id, 'email': tm.user.email, 'role': tm.role} for tm in team.members]
    return jsonify(members)

@app.route('/github-callback')
def github_callback():
    return render_template('auth.html')

@app.route('/github-login', methods=['POST'])
def github_login():
    code = request.json.get('code')
    
    # Exchange code for access token
    response = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': os.getenv('GITHUB_CLIENT_ID'),
            'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
            'code': code
        },
        headers={'Accept': 'application/json'}
    )
    
    access_token = response.json().get('access_token')
    
    # Get user info
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'token {access_token}'}
    )
    user_data = user_response.json()
    
    # Get user email
    email_response = requests.get(
        'https://api.github.com/user/emails',
        headers={'Authorization': f'token {access_token}'}
    )
    email_data = email_response.json()
    email = next((email['email'] for email in email_data if email['primary']), None)
    
    # Check if user exists, if not create a new user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, password=generate_password_hash('github_oauth_user'))
        db.session.add(user)
        db.session.commit()
    
    # Log in the user
    session['user_id'] = user.id
    
    return jsonify({"message": "Logged in successfully", "redirect": "/dashboard/home", "email": email}), 200

@app.route("/static/styles.css")
def serve_css():
    return send_from_directory('static', 'styles.css')

# Add these imports if they're not already present
from flask import request, jsonify
from datetime import datetime

# Add this global variable to store API usage data
api_usage = {}

# Add this decorator to the routes that you want to track
def track_api_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        endpoint = request.endpoint
        if endpoint not in api_usage:
            api_usage[endpoint] = []
        api_usage[endpoint].append(datetime.now())
        return func(*args, **kwargs)
    return wrapper

# Add this new route to retrieve API usage data
@app.route('/api/analytics', methods=['GET'])
def get_api_analytics():
    analytics = {}
    for endpoint, calls in api_usage.items():
        analytics[endpoint] = len(calls)
    return jsonify(analytics)

# Apply the decorator to the API routes you want to track
@app.route('/api/some_endpoint', methods=['POST'])
@track_api_usage
def some_api_endpoint():
    # Your existing code here
    pass

# Repeat for other API endpoints you want to track

# Add this route temporarily to generate test data
@app.route("/generate_test_analytics")
@login_required
def generate_test_analytics():
    user_id = session["user_id"]
    for i in range(50):  # Generate 50 test entries
        analytics = Analytics(
            user_id=user_id,
            api_key="test_key",
            endpoint="/test",
            response_time=random.uniform(0.1, 2.0),
            status_code=random.choice([200, 200, 200, 400, 500]),
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 29))
        )
        db.session.add(analytics)
    db.session.commit()
    return "Test analytics data generated"

# Add this near the top of your file, with other imports
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Add these new routes
@app.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No user found with that email address"}), 404

    # Generate a timed token
    token = s.dumps(email, salt='password-reset-salt')

    # Send password reset email
    reset_url = url_for('reset_password', token=token, _external=True)
    send_password_reset_email(email, reset_url)

    return jsonify({"message": "Password reset link sent to your email"}), 200

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires after 1 hour
    except:
        return render_template('auth.html', error="The password reset link is invalid or has expired.")

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return render_template('auth.html', error="Passwords do not match.")

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return render_template('auth.html', message="Your password has been reset successfully. You can now log in with your new password.")
        else:
            return render_template('auth.html', error="User not found.")

    return render_template('reset_password.html', token=token)

# Add this function to send the password reset email
def send_password_reset_email(email, reset_url):
    subject = "Password Reset Request"
    body = f"""
    Hello,

    You have requested to reset your password. Please click on the link below to reset your password:

    {reset_url}

    If you did not request this, please ignore this email and your password will remain unchanged.

    Best regards,
    The Chatcat Team
    """

    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)

# Add this new function to get the Hume AI access token
def get_hume_access_token():
    auth = f"{HUME_API_KEY}:{HUME_SECRET_KEY}"
    encoded_auth = base64.b64encode(auth.encode()).decode()
    resp = httpx.request(
        method="POST",
        url="https://api.hume.ai/oauth2-cc/token",
        headers={"Authorization": f"Basic {encoded_auth}"},
        data={"grant_type": "client_credentials"},
    )
    return resp.json()['access_token']

# Add this new route for the playground page
@app.route('/playground')
def playground():
    try:
        return render_template('playground.html')
    except Exception as e:
        app.logger.error(f"Error rendering playground template: {str(e)}")
        return f"Error: {str(e)}", 500

# Add this new route for voice chat processing
@app.route('/voice_chat', methods=['POST'])
def voice_chat():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    # Get Hume AI access token
    access_token = get_hume_access_token()

    # Send audio to Hume AI for processing
    files = {'file': ('audio.wav', audio_file, 'audio/wav')}
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = httpx.post(
        'https://api.hume.ai/v0/batch/jobs',
        files=files,
        data={'models': 'prosody'},
        headers=headers
    )

    if response.status_code != 200:
        return jsonify({'error': 'Error processing audio'}), 500

    job_id = response.json()['job_id']

    # Poll for job completion
    while True:
        job_status = httpx.get(
            f'https://api.hume.ai/v0/batch/jobs/{job_id}',
            headers=headers
        )
        if job_status.json()['state'] == 'completed':
            break
        time.sleep(1)

    # Get job results
    results = httpx.get(
        f'https://api.hume.ai/v0/batch/jobs/{job_id}/results',
        headers=headers
    )

    # Process the results and return a response
    emotions = results.json()[0]['results']['predictions'][0]['prosody']['emotions']
    top_emotion = max(emotions, key=lambda x: x['score'])
    
    return jsonify({'response': f"The dominant emotion detected is {top_emotion['name']} with a score of {top_emotion['score']:.2f}"})

@app.route('/test')
def test():
    return render_template('test.html')

@app.route("/api/website-info")
def get_website_info():
    api_key = request.args.get("api_key")
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    api_key_data = APIKey.query.filter_by(key=api_key).first()
    if not api_key_data:
        return jsonify({"error": "Invalid API key"}), 400

    user = User.query.get(api_key_data.user_id)
    website_info = WebsiteInfo.query.filter_by(user_id=user.id).first()

    if not website_info:
        return jsonify({"error": "Website information not found"}), 404

    return jsonify({
        "website_name": website_info.name,
        "description": website_info.description,
        "features": website_info.features.split(',')
    })

@app.route("/api/faq")
def get_faq():
    api_key = request.args.get("api_key")
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    api_key_data = APIKey.query.filter_by(key=api_key).first()
    if not api_key_data:
        return jsonify({"error": "Invalid API key"}), 400

    user = User.query.get(api_key_data.user_id)
    faq_items = FAQ.query.filter_by(user_id=user.id).order_by(FAQ.order).all()

    return jsonify({
        "faq": [{"question": item.question, "answer": item.answer} for item in faq_items]
    })

@app.route("/dashboard/faq", methods=["GET", "POST"])
@login_required
def manage_faq():
    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")
        new_faq = FAQ(user_id=session["user_id"], question=question, answer=answer)
        db.session.add(new_faq)
        db.session.commit()
        flash("FAQ item added successfully", "success")
        return redirect(url_for("dashboard_section", section="faq-management"))

    faq_items = FAQ.query.filter_by(user_id=session["user_id"]).order_by(FAQ.order).all()
    return render_template("dashboard.html", active_section="faq-management", faq_items=faq_items)

@app.route("/dashboard/website-info", methods=["GET", "POST"])
@login_required
def manage_website_info():
    website_info = WebsiteInfo.query.filter_by(user_id=session["user_id"]).first()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        features = request.form.get("features")

        if website_info:
            website_info.name = name
            website_info.description = description
            website_info.features = features
        else:
            new_info = WebsiteInfo(user_id=session["user_id"], name=name, description=description, features=features)
            db.session.add(new_info)

        db.session.commit()
        flash("Website information updated successfully", "success")
        return redirect(url_for("dashboard_section", section="website-info"))

    return render_template("dashboard.html", active_section="website-info", website_info=website_info)

@app.route("/delete_faq", methods=["POST"])
@login_required
def delete_faq():
    faq_id = request.json.get('faq_id')
    faq = FAQ.query.get(faq_id)
    if faq and faq.user_id == session["user_id"]:
        db.session.delete(faq)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route("/update_faq_order", methods=["POST"])
@login_required
def update_faq_order():
    faq_order = request.json.get('faq_order')
    if faq_order:
        for index, faq_id in enumerate(faq_order):
            faq = FAQ.query.get(faq_id)
            if faq and faq.user_id == session["user_id"]:
                faq.order = index
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

# Add this import at the top of the file
import random

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Schedule the deletion of old conversations every 24 hours
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=delete_old_conversations, trigger="interval", hours=24)
    scheduler.start()
    
    app.run(debug=True, port=5410)