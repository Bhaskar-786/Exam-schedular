from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import sqlite3
import pandas as pd
from fpdf import FPDF
import os
from main import (main)
from dataProcessing.prc import (
    process_student_files,
    build_courses_and_students,
    update_pairs_with_common_courses,
    save_json,
    load_pairs_from_csv
)
from dataProcessing.lecture_hall_processing import lecture_hall_processing


app = Flask(__name__)
CORS(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = "super-secret-key-new"  # Change in production
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# Token Blacklist
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist

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

def nb_lines(pdf, text, col_width):
    # Add a temporary page to calculate the height
    tmp = FPDF()
    tmp.set_auto_page_break(auto=True, margin=15)
    tmp.add_page()
    tmp.set_font("Arial", size=11)
    tmp.set_xy(0, 0)
    tmp.multi_cell(col_width, 8, text)  # Create multi-cell
    return tmp.get_y()  # Return the y position, which will give us the height

def convert_csv_to_pdf_seatingplan(csv_path="seating_plan.csv", pdf_path="seating_plan.pdf"):
    df = pd.read_csv(csv_path, header=None, engine='python')
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Add centered heading

    pdf.image("img/IIT_(ISM)_Dhanbad_Logo.svg.png", x=10, y=8, w=25)

    # Move to the right and set position for centered heading
    pdf.set_xy(35, 10)
    pdf.set_font("Arial", "B", 15)
    pdf.set_text_color(0, 51, 102)  # Dark blue
    pdf.cell(0, 10, txt="Indian Institute of Technology (Indian School of Mines), Dhanbad", ln=True, align="C")
    #pdf.set_x(35)
    # Add main section title
    pdf.set_font("Arial", "BU", 13)  # Bold + Underlined
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt="Seating Plan", ln=True, align="C")

    pdf.ln(5)

    #pdf.set_font("Arial", "B", 16)
    #pdf.cell(0, 10, txt="Seating Plan", ln=True, align="C")
    #pdf.ln(5)
    #pdf.set_font("Arial", size=11)

    row_count = df.shape[0]
    i = 0

    while i < row_count:
        row = df.iloc[i]

        # Detect start of a new slot (Day X - Slot Y)
        if isinstance(row[0], str) and row[0].startswith("Day") and isinstance(row[1], str) and row[1].strip().startswith("Slot"):
            day = row[0].strip()
            slot = row[1].strip()
            pdf.ln(5)  # space above the bordered line
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(0, 51, 102)      # Deep navy blue
            pdf.set_text_color(255, 255, 255)   # White text


            # Draw a full-width bordered cell
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.rect(x, y, 190, 9, style='FD')  # Full line border (A4 width with margins)
            pdf.cell(95, 9, txt=day, ln=0, align="L", fill=True)
            pdf.cell(95, 9, txt=slot, ln=1, align="R", fill=True)
            pdf.ln(0)

            #pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(0, 0, 0)
            #pdf.cell(0, 8, txt=row[0], ln=True)
            i += 1

            # Check and print column headers
            if i < row_count and str(df.iloc[i][0]) == "Course Code":
                pdf.set_font("Arial", "B", 10)
                pdf.set_fill_color(200, 200, 200)
                pdf.cell(50, 8, "Course Code", border=1, fill=True)
                pdf.cell(50, 8, "Lecture Hall", border=1, fill=True)
                pdf.cell(45, 8, "Position", border=1, fill=True)
                pdf.cell(45, 8, "No. of seats", border=1, fill=True)
                pdf.ln()
                i += 1

            # Print course data
            pdf.set_font("Arial", size=10)
            last_course_code = None
            color_index = 0
            fill_colors = [
                (255, 220, 235),  # Soft Pink
                (220, 240, 255)   # Soft Sky Blue
            ]
            while i < row_count and not (isinstance(df.iloc[i][0], str) and df.iloc[i][0].startswith("Day")):
                row = df.iloc[i]
                # Skip empty lines
                if pd.isna(row[0]):
                    i += 1
                    continue
                course_code = str(row[0])
                lecture_hall = str(row[1])
                position = str(row[2])
                no_of_seats = str(row[3])

                current_course_code = str(row[0])
                if current_course_code != last_course_code:
                    color_index = 1 - color_index  # Toggle color
                    last_course_code = current_course_code

                pdf.set_fill_color(*fill_colors[color_index])

                pdf.cell(50, 8, course_code, border=1, fill=True)
                pdf.cell(50, 8, lecture_hall, border=1, fill=True)
                pdf.cell(45, 8, position, border=1, fill=True)
                pdf.cell(45, 8, no_of_seats, border=1, fill=True)
                pdf.ln()
                i += 1
        else:
            i += 1

    pdf.output(pdf_path)
    print(f"Seating plan PDF generated at '{pdf_path}'.")

def convert_csv_to_pdf_venue(csv_path="lecture_hall_schedule.csv", pdf_path="lecture_hall_schedule.pdf"):
    df = pd.read_csv(csv_path, header=None, engine='python')

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Add centered heading
    # Add centered and styled heading
    # Add the IIT ISM logo
    # Add IIT(ISM) logo
    # Add IIT(ISM) logo
    # Add IIT(ISM) logo
    # Add IIT(ISM) logo
    pdf.image("img/IIT_(ISM)_Dhanbad_Logo.svg.png", x=10, y=8, w=25)

    # Move to the right and set position for centered heading
    pdf.set_xy(35, 10)
    pdf.set_font("Arial", "B", 15)
    pdf.set_text_color(0, 51, 102)  # Dark blue
    pdf.cell(0, 10, txt="Indian Institute of Technology (Indian School of Mines), Dhanbad", ln=True, align="C")
    #pdf.set_x(35)
    # Add main section title
    pdf.set_font("Arial", "BU", 13)  # Bold + Underlined
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt="Venue Allocation", ln=True, align="C")

    pdf.ln(5)


    #pdf.set_font("Arial", "B", 16)
    #pdf.cell(0, 10, txt="Venue Allocation", ln=True, align="C")
    #pdf.ln(5)

    row_count = df.shape[0]
    i = 0

    while i < row_count:
        row = df.iloc[i]
        if isinstance(row[0], str) and row[0].startswith("Day") and isinstance(row[1], str) and row[1].strip().startswith("Slot"):
            # Print Day X - Slot Y

            day = row[0].strip()
            slot = row[1].strip()
            pdf.ln(5)  # space above the bordered line
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(0, 102, 102)     # Teal
            pdf.set_text_color(255, 255, 255)   # White text

            # Draw a full-width bordered cell
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.rect(x, y, 190, 9, style='FD')  # Full line border (A4 width with margins)
            pdf.cell(95, 9, txt=day, ln=0, align="L", fill=True)
            pdf.cell(95, 9, txt=slot, ln=1, align="R", fill=True)
            pdf.ln(0)

            #pdf.set_font("Arial", "B", 12)
            #pdf.set_text_color(0, 0, 0)
            #pdf.cell(0, 8, txt=row[0], ln=True)
            i += 1
            pdf.set_text_color(0, 0, 0)
            # Print table header (Course Code, No. of Students, Venue)
            if i < row_count and str(df.iloc[i][0]) == "Course Code":
                pdf.set_font("Arial", "B", 10)
                pdf.set_fill_color(200, 200, 200)
                pdf.cell(60, 8, "Course Code", border=1, fill=True)
                pdf.cell(40, 8, "No. of Students", border=1, fill=True)
                pdf.cell(90, 8, "Venue", border=1, fill=True)
                pdf.ln()
                i += 1

            # Print table rows
            pdf.set_font("Arial", size=10)
            pdf.set_fill_color(210, 255, 240)
            while i < row_count and not str(df.iloc[i][0]).startswith("Day"):
                # Skip empty lines
                if pd.isna(df.iloc[i][0]):
                    i += 1
                    continue
                course_code = str(df.iloc[i][0])
                no_of_students = str(df.iloc[i][1])
                venue = str(df.iloc[i][2])

                # Use multi_cell for course code, number of students, and venue
                # To keep all cells consistent in height, we calculate the number of lines for each cell
                # Calculate height based on venue


                # Calculate the max number of lines needed for the current row
                #course_code_lines = pdf.get_string_width(course_code) // 60 + 1  # Assuming 60 width per cell
                #students_lines = pdf.get_string_width(no_of_students) // 40 + 1  # Assuming 40 width per cell
                #venue_lines = pdf.get_string_width(venue) // 90 + 1  # Assuming 90 width per cell

                # Calculate the height of the row based on the wrapped venue
                row_height = nb_lines(pdf, venue, 90)
                #row_height = venue_lines * 10
                if pdf.get_y() + row_height > 270:
                    pdf.add_page()
                # The row height is the max number of lines across all columns
                #row_height = max(course_code_lines, students_lines, venue_lines) * 10  # Set height to 10 per line
                
                x = pdf.get_x()
                y = pdf.get_y()
                pdf.rect(x, y, 60, row_height, style='FD')
                pdf.rect(x + 60, y, 40, row_height, style='FD')
                pdf.rect(x + 100, y, 90, row_height, style='FD')

                pdf.multi_cell(60, 8 , course_code, border=0)
                pdf.set_xy(x + 60, y)
                pdf.multi_cell(40, 8 , no_of_students, border=0)
                pdf.set_xy(x + 100, y)
                pdf.multi_cell(90, 8, venue, border=0)
                pdf.set_y(y + row_height)

                i += 1
        else:
            i += 1

    pdf.output(pdf_path)


    
def convert_csv_to_pdf(csv_path, pdf_path):
    df = pd.read_csv(csv_path)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Add centered heading
    pdf.image("img/IIT_(ISM)_Dhanbad_Logo.svg.png", x=10, y=8, w=25)

    # Move to the right and set position for centered heading
    pdf.set_xy(35, 10)
    pdf.set_font("Arial", "B", 15)
    pdf.set_text_color(0, 51, 102)  # Dark blue
    pdf.cell(0, 10, txt="Indian Institute of Technology (Indian School of Mines), Dhanbad", ln=True, align="C")
    #pdf.set_x(35)
    # Add main section title
    pdf.set_font("Arial", "BU", 13)  # Bold + Underlined
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt="Exam Schedule", ln=True, align="C")

    pdf.ln(5)
    pdf.ln(5)

    #pdf.set_font("Arial", "B", 16)
    #pdf.cell(0, 10, txt="Exam Schedule", ln=True, align="C")
    #pdf.ln(5)

    # Adding table headers
    #col_width = pdf.w / (len(df.columns) + 1)
    col_width = 47.5
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(200, 200, 200)
    for column in df.columns:
        pdf.cell(col_width, 8, column, border=1, fill=True)
    pdf.ln()

    # Adding table rows
    pdf.set_fill_color(220, 240, 255)
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        for value in row:
            pdf.cell(col_width, 8, str(value), border=1, fill=True)
        pdf.ln()

    pdf.output(pdf_path)

# LOGIN API
"""
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
    """

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

    access_token = create_access_token(identity=username)
    return jsonify({"message": "Login successful", "access_token": access_token}), 200


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"message": "Logout successful"}), 200


@app.route('/')
def home():
    return "Welcome to the Exam Scheduler API!"

# Define the route to process uploaded files
@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_files():
    try:
        # Define and ensure the target directory exists
        data_dir = os.path.abspath("dataProcessing")
        os.makedirs(data_dir, exist_ok=True)

        student_file_nep = request.files.get('student_file1')
        student_file_cbcs = request.files.get('student_file2')
        hall_file = request.files.get('hall_file')
        common_file = request.files.get('common_file')
        
  
        if not hall_file or not allowed_file(hall_file.filename):
            return jsonify({"message": "Please upload a valid Lecture Hall Details file!"}), 400
        if not student_file_nep or not allowed_file(student_file_nep.filename):
            return jsonify({"message": "Please upload a valid NEP Student-Course file!"}), 400
        #if not common_file or not allowed_file(common_file.filename):
            #return jsonify({"message": "Please upload a valid common.csv file!"}), 400
        
        
        lecture_hall_processing(hall_file)
        
        
        #save nep file
        nep_path = os.path.join(data_dir, "nep.csv")
        student_file_nep.save(nep_path)
        
        # Save common file if valid
        common_path = None
        if common_file and allowed_file(common_file.filename):
            common_path = os.path.join(data_dir, "common.csv")
            common_file.save(common_path)
        
        # Save CBCS file if valid
        cbcs_path = None
        if student_file_cbcs and allowed_file(student_file_cbcs.filename):
            cbcs_path = os.path.join(data_dir, "cbcs.csv")
            student_file_cbcs.save(cbcs_path)
        
        # Call our processing function to process student files
        courses_count = process_student_files(nep_path, common_path, cbcs_path)
        
        return jsonify({"message": "Files processed successfully!", "courses_count": courses_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Define the route to generate the schedule
@app.route('/api/schedule', methods=['POST'])
@jwt_required()
def generate_schedule():
    try:
        mxd = request.form.get('max_days')
        mxs = request.form.get('max_slots')
        max_days = int(mxd)
        max_slots = int(mxs)
        main(max_days, max_slots)  # calling the main scheduling function 
        convert_csv_to_pdf('exam_schedule.csv', 'exam_schedule.pdf')
        convert_csv_to_pdf_venue('lecture_hall_schedule.csv', 'lecture_hall_schedule.pdf')
        convert_csv_to_pdf_seatingplan('seating_plan.csv', 'seating_plan.pdf')
        # Returning the generated schedule as a response
        return jsonify({"message": "Schedule generated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to serve the schedule file
@app.route('/api/schedule/download/<file_type>/<file_name>', methods=['GET'])
@jwt_required()
def download_schedule(file_type, file_name):
    try:
        # If it's a schedule file or hall accommodation file, handle both.
        if file_type == 'csv' or file_type == 'pdf':
            # Define valid file names for both schedule and hall accommodation
            if file_name == "schedule":
                file_name = f'exam_schedule.{file_type}'
            elif file_name == "venue_allocation":
                file_name = f'lecture_hall_schedule.{file_type}'
            elif file_name == "seating_plan":
                file_name = f'seating_plan.{file_type}'
            else:
                return jsonify({"error": "Invalid file name"}), 400
            
            return send_file(file_name, as_attachment=True)
        else:
            return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/schedule/view", methods=["GET"])
@jwt_required()
def view_schedule_pdf():
    pdf_path = r"exam_schedule.pdf"
    try:
        if not os.path.exists(pdf_path):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(pdf_path, mimetype="application/pdf", as_attachment=False)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/hall/view", methods=["GET"])
@jwt_required()
def view_hall_pdf():
    pdf_path = r"lecture_hall_schedule.pdf"
    try:
        if not os.path.exists(pdf_path):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(pdf_path, mimetype="application/pdf", as_attachment=False)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/seatingplan/view", methods=["GET"])
@jwt_required()
def view_seatingplan_pdf():
    pdf_path = r"seating_plan.pdf"
    try:
        if not os.path.exists(pdf_path):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(pdf_path, mimetype="application/pdf", as_attachment=False)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# When token is expired
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Token has expired"}), 401

# When token is revoked/blacklisted
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Token has been revoked"}), 401

# When no token is provided in request
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Missing access token"}), 401

# When token is invalid or malformed
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token"}), 422

# Optional: token freshness expired (if using fresh tokens)
@jwt.needs_fresh_token_loader
def fresh_token_required_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Fresh token required"}), 401


if __name__ == "__main__":
    app.run(debug=True)
