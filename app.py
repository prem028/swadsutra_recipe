import os
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, request, render_template, redirect, url_for, flash, session
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
from tensorflow.keras.applications.resnet50 import preprocess_input
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

# Initialize Flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Use environment variable in production

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '<smtp_username>')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '<smtp_Passwprd>')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///users.db')

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  verification_token TEXT,
                  is_verified BOOLEAN DEFAULT 0)''')
    conn.commit()
    conn.close()

def send_verification_email(email, token):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = "Verify your Swadsutra Food account"
    
    # Get the base URL from environment variable or use localhost
    base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
    verification_url = f"{base_url}/verify/{token}"
    
    body = f"""
    Hello!
    
    Please verify your Swadsutra Food account by clicking the link below:
    
    {verification_url}
    
    If you didn't create an account, you can safely ignore this email.
    
    Best regards,
    Swadsutra Food Team
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"Attempting to send email to: {email}")
        print(f"Using SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"Using username: {SMTP_USERNAME}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

@app.route("/verify/<token>")
def verify_email(token):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE verification_token = ?", (token,)).fetchone()
    
    if user:
        c.execute("UPDATE users SET is_verified = 1, verification_token = NULL WHERE id = ?", (user[0],))
        conn.commit()
        flash('Email verified successfully! You can now login.', 'success')
    else:
        flash('Invalid or expired verification token.', 'error')
    
    conn.close()
    return redirect(url_for('login'))

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Load trained model
model = tf.keras.models.load_model("model/food_classifier_resnet50.h5")
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

with open("model/class.txt", "r") as f:
    class_labels = [line.strip() for line in f.readlines() if line.strip()]
print(f"Class Labels: {class_labels}")

# Load recipe dataset
recipe_data = pd.read_csv("dataset/recipe_model.csv", encoding="ISO-8859-1")
recipe_data["Food_Item"] = recipe_data["Food_Item"].str.strip()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Initialize database
init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def classify_food(img_path):
    img_array = preprocess_image(img_path)
    preds = model.predict(img_array)
    print(f"Prediction Raw Output: {preds}")
    class_index = np.argmax(preds)
    print(f"Predicted Class Index: {class_index}")
    if class_index >= len(class_labels):
        return "Unknown Food"
    food_name = class_labels[class_index-1]
    print(f"Predicted Food Name: {food_name}")
    return food_name

def get_recipe(food_name):
    print(f"Looking for recipe of: {food_name}")
    match = recipe_data[recipe_data["Food_Item"].str.contains(food_name, case=False, na=False)]
    if not match.empty:
        print(f"Found Recipe: {match['Recipe'].values[0]}")
        return match["Recipe"].values[0]
    else:
        print("Recipe not found.")
        return "Recipe not found."

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            if not user[5]:  # Check if email is verified
                flash('Please verify your email before logging in.', 'error')
                return redirect(url_for('login'))
            
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if username or email already exists
        if c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email)).fetchone():
            flash('Username or email already exists', 'error')
            conn.close()
            return redirect(url_for('signup'))
        
        # Create new user with verification token
        hashed_password = generate_password_hash(password)
        verification_token = secrets.token_urlsafe(32)
        c.execute("INSERT INTO users (username, email, password, verification_token) VALUES (?, ?, ?, ?)",
                 (username, email, hashed_password, verification_token))
        conn.commit()
        conn.close()
        
        # Send verification email
        if send_verification_email(email, verification_token):
            flash('Account created! Please check your email to verify your account.', 'success')
        else:
            flash('Account created but there was an error sending the verification email. Please contact support.', 'error')
        
        return redirect(url_for('login'))
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "" or not allowed_file(file.filename):
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        food_name = classify_food(filepath)
        recipe = get_recipe(food_name)

        return render_template("index.html", food_name=food_name, recipe=recipe, image=filename)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
