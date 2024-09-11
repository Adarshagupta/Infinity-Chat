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
from datetime import datetime
import time
from alembic import op
import sqlalchemy as sa
from functools import wraps

# Load environment variables from .env file
load_dotenv()

# Get the API keys from the environment variables
together_api_key = os.getenv("TOGETHER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not together_api_key:
    raise ValueError("No Together API key set for TOGETHER_API_KEY")
if not openai_api_key:
    raise ValueError("No OpenAI API key set for OPENAI_API_KEY")

together_client = Together(api_key=together_api_key)
openai_client = OpenAI(api_key=openai_api_key, base_url="https://api.aimlapi.com")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_keys = db.relationship("APIKey", backref="user", lazy=True)
    custom_prompts = db.relationship("CustomPrompt", backref="user", lazy=True)
    fine_tune_jobs = db.relationship('FineTuneJob', backref='user', lazy=True)


# APIKey model
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    llm = db.Column(db.String(50), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    fine_tune_jobs = db.relationship('FineTuneJob', backref='api_key', lazy=True)


# CustomPrompt model
class CustomPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    prompt = db.Column(db.String(255), nullable=False)
    response = db.Column(db.Text, nullable=False)


# Add this after the CustomPrompt model
class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    endpoint = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float, nullable=False)
    status_code = db.Column(db.Integer, nullable=False)


# New database models
class AIModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    api_endpoint = db.Column(db.String(200), nullable=False)
    documentation_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ModelReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey("ai_model.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Add this new model for fine-tuning
class FineTuneJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_key.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    training_file = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=True)


def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join([p.text for p in soup.find_all("p")])


def generate_integration_code(api_key):
    return f"""
<!-- AI Chatbot Integration -->
<script src="https://chatcat-moo7.onrender.com/chatbot.js?api_key={api_key}"></script>
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
        db.session.query("1").from_statement(text("SELECT 1")).all()
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


@app.route("/project")
def projects():
    return render_template("products.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        return jsonify({"message": "Logged in successfully"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/process_url", methods=["POST"])
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


# Modify the chat route to improve memory handling
@app.route("/chat", methods=["POST"])
@limiter.limit("50 per minute")
def chat():
    start_time = time.time()
    try:
        user_input = request.json.get("input")
        api_key = request.json.get("api_key")

        if not user_input or not api_key:
            return jsonify({"error": "Input and API key are required"}), 400

        api_key_data = APIKey.query.filter_by(key=api_key).first()
        if not api_key_data:
            return jsonify({"error": "Invalid API key"}), 400

        # Fetch the extracted text associated with this API key
        context = api_key_data.extracted_text

        # Fetch custom prompts for the user
        custom_prompts = CustomPrompt.query.filter_by(user_id=api_key_data.user_id).all()

        # Initialize or retrieve conversation history
        conversation_history = session.get(f"conversation_history_{api_key}", [])

        # Append user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

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
- Present product details clearly (name, price, brief description)
- Mention any current promotions or deals
- Suggest complementary items
- Guide users towards making a purchase decision

Custom prompts:
{' '.join([f'- {prompt.prompt}: {prompt.response}' for prompt in custom_prompts])}

If you need more information to answer accurately, ask the user a clarifying question.""",
            }
        ] + conversation_history[-5:]  # Include last 5 messages for context

        logger.info(f"Sending request to AI service with input: {user_input}")

        ai_response = get_ai_response(api_key_data.llm, messages)

        logger.info(f"Received response from AI service: {ai_response}")

        # Append AI response to conversation history
        conversation_history.append({"role": "assistant", "content": ai_response})

        # Save updated conversation history to session
        session[f"conversation_history_{api_key}"] = conversation_history
        session.modified = True  # Ensure session is saved

        # Process the AI response for e-commerce functionality
        processed_response = process_ecommerce_response(ai_response)

        # Record analytics
        end_time = time.time()
        response_time = end_time - start_time
        analytics = Analytics(
            user_id=api_key_data.user_id,
            api_key=api_key,
            endpoint="/chat",
            response_time=response_time,
            status_code=200,
        )
        db.session.add(analytics)
        db.session.commit()
        app.logger.info(
            f"Recorded analytics for user_id: {api_key_data.user_id}, api_key: {api_key}"
        )

        return jsonify(processed_response)
    except Exception as e:
        app.logger.error(f"Error in chat route: {str(e)}", exc_info=True)

        # Record analytics for error case
        end_time = time.time()
        response_time = end_time - start_time
        analytics = Analytics(
            user_id=api_key_data.user_id if "api_key_data" in locals() else None,
            api_key=api_key if "api_key" in locals() else None,
            endpoint="/chat",
            response_time=response_time,
            status_code=500,
        )
        db.session.add(analytics)
        db.session.commit()
        app.logger.info(f"Recorded error analytics for api_key: {api_key}")

        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


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
    if llm_type == "together":
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=messages,
            max_tokens=100,
            temperature=2,
            top_p=1,
            top_k=100,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
        )
        return response.choices[0].message.content
    elif llm_type == "openai":
        response = openai_client.chat.completions.create(
            model="gpt-4", messages=messages, max_tokens=128, temperature=0.7
        )
        return response.choices[0].message.content
    else:
        raise ValueError("Invalid LLM specified")


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


@app.route("/user/api_keys", methods=["GET"])
def get_user_api_keys():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.get(session["user_id"])
    api_keys = [{"api_key": key.key, "llm": key.llm} for key in user.api_keys]
    return jsonify({"api_keys": api_keys})


# Add this new route to retrieve analytics data
@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    user_id = session["user_id"]
    analytics = Analytics.query.filter_by(user_id=user_id).order_by(Analytics.timestamp.desc()).limit(100).all()
    
    analytics_data = [
        {
            "api_key": a.api_key,
            "endpoint": a.endpoint,
            "timestamp": a.timestamp.isoformat(),
            "response_time": a.response_time,
            "status_code": a.status_code,
        }
        for a in analytics
    ]
    
    return jsonify(analytics_data)

@app.route("/test/insert_analytics", methods=["GET"])
def test_insert_analytics():
    try:
        test_analytics = Analytics(
            user_id=1,  # Replace with a valid user_id
            api_key="test_key",
            endpoint="/test",
            response_time=0.5,
            status_code=200,
        )
        db.session.add(test_analytics)
        db.session.commit()
        return jsonify({"message": "Test analytics data inserted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error in test_insert_analytics: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while inserting test data"}), 500


@app.route("/test_apis")
def test_apis():
    together_result = "Failed"
    openai_result = "Failed"

    try:
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
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


# Create a decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/update_profile", methods=["POST"])
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
@app.route("/api")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    api_keys = user.api_keys
    custom_prompts = user.custom_prompts

    # Fetch analytics data
    analytics = (
        Analytics.query.filter_by(user_id=user.id)
        .order_by(Analytics.timestamp.desc())
        .limit(100)
        .all()
    )

    analytics_data = [
        {
            "api_key": a.api_key,
            "endpoint": a.endpoint,
            "timestamp": a.timestamp.isoformat(),
            "response_time": a.response_time,
            "status_code": a.status_code,
        }
        for a in analytics
    ]

    return render_template(
        "dashboard.html",
        user=user,
        api_keys=api_keys,
        custom_prompts=custom_prompts,
        analytics_data=analytics_data,
    )


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


@app.route("/delete_api_key", methods=["POST"])
@login_required
def delete_api_key():
    api_key_id = request.form.get("api_key_id")
    api_key = APIKey.query.get(api_key_id)
    if api_key and api_key.user_id == session["user_id"]:
        db.session.delete(api_key)
        db.session.commit()
        flash("API key deleted successfully", "success")
    else:
        flash("API key not found or you do not have permission to delete it", "error")

    return redirect(url_for("dashboard"))


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

    return redirect(url_for("dashboard"))


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
            "https://chatcat-moo7.onrender.com/chat",
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
            "average_rating": get_average_rating(model_id),
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
    
@app.route("/auth")
def auth():
    return render_template("auth.html")

@app.route('/api/fine-tune', methods=['POST'])
@login_required
def start_fine_tuning():
    data = request.json
    api_key_id = data.get('api_key_id')
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5410)
