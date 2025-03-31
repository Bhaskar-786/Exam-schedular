from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import sqlite3
import pandas as pd
from fpdf import FPDF
import os
from main import (main)

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT, password TEXT)''')
    conn.commit()
    conn.close()

init_db()  # Initialize DB

# Helper function to fetch user from DB
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# SIGNUP API
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 400
    
ALLOWED_EXTENSIONS = {'csv'}  # Allowed file types

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
def convert_csv_to_pdf(csv_path, pdf_path):
    df = pd.read_csv(csv_path)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adding table headers
    col_width = pdf.w / (len(df.columns) + 1)
    for column in df.columns:
        pdf.cell(col_width, 10, column, border=1)
    pdf.ln()

    # Adding table rows
    for _, row in df.iterrows():
        for value in row:
            pdf.cell(col_width, 10, str(value), border=1)
        pdf.ln()

    pdf.output(pdf_path)

# LOGIN API
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = get_user(username)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user[1], password):
        return jsonify({"message": "Invalid password"}), 401

    return jsonify({"message": "Login successful", "token": "fake-jwt-token"}), 200

@app.route('/')
def home():
    return "Welcome to the Exam Scheduler API!"

# Define the route to process uploaded files
@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        # Process the files here as per your existing logic
        student_file1 = request.files.get('student_file1')
        student_file2 = request.files.get('student_file2')
        if student_file1 and student_file2 and allowed_file(student_file1.filename) and allowed_file(student_file2.filename):
            # Call your existing file processing functions here
            #process_files(student_file, hall_file)  # Make sure to modify this function
            return jsonify({"message": "Files processed successfully!"}), 200
        else:
            return jsonify({"message": "Please upload both the student files!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define the route to generate the schedule
@app.route('/api/schedule', methods=['POST'])
def generate_schedule():
    try:
        main()
        schedule_data = 'exam_schedule.csv'  # Modify accordingly with real schedule data
        hall_allocation_data = 'exam_schedule.csv'  # Modify accordingly with hall allocation data
        
        # Returning the generated schedule as a response
        return jsonify({
            "schedule": schedule_data,
            "hall_allocation": hall_allocation_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to serve the schedule file
@app.route('/api/schedule/download/<file_type>/<file_name>', methods=['GET'])
def download_schedule(file_type, file_name):
    try:
        # If it's a schedule file or hall accommodation file, handle both.
        if file_type == 'csv':
            # Define valid file names for both schedule and hall accommodation
            if file_name == "schedule":
                file_name = f'exam_schedule.{file_type}'
            elif file_name == "hall_accommodation":
                file_name = f'exam_schedule.{file_type}'
            else:
                return jsonify({"error": "Invalid file name"}), 400

            return send_file(file_name, as_attachment=True)
        elif file_type == 'pdf':
            if file_name == "schedule":
                file_name = f'exam_schedule.csv'
                output_name = 'exam_schedule.pdf'
            elif file_name == "hall_accommodation":
                file_name = f'exam_schedule.csv'
                output_name = 'exam_schedule.pdf'
            else:
                return jsonify({"error": "Invalid file name"}), 400
            convert_csv_to_pdf(file_name, output_name)
            return send_file(output_name, as_attachment=True)
        else:
            return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
