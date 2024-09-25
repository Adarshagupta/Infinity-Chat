from flask import Blueprint, request, jsonify, session, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utils import send_otp

bp = Blueprint('auth', __name__)

@bp.route("/auth")
@bp.route("/login")
def auth():
    return render_template('auth.html')

@bp.route('/send-otp', methods=['POST'])
def send_otp_route():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        send_otp(email)
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to send OTP"}), 500

@bp.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    password = request.json.get("password")
    otp = request.json.get("otp")

    if not email or not password or not otp:
        return jsonify({"error": "Email, password, and OTP are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        return jsonify({"message": "Logged in successfully"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200