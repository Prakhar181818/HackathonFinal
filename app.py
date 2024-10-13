from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import os
import io
from PIL import Image
import google.generativeai as genai

load_dotenv()  # Load environment variables

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Set a secret key for session management

# Configure the Google Gemini AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the function to get the Gemini response
def get_gemini_response(input_text, image):
    model = genai.GenerativeModel('gemini-pro-vision')

    # Check if the image is already in the correct format
    if isinstance(image, Image.Image):  # Check if it's a PIL Image
        # Generate response
        if input_text != "":
            response = model.generate_content([input_text, image])
        else:
            response = model.generate_content(image)
        
        return response.text
    else:
        raise ValueError("Image must be a PIL Image object.")

# In-memory user storage for demonstration (replace with a database in production)
users = {}

@app.route('/')
def home():
    return render_template('\flask_app\templates\home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            return redirect(url_for('login'))
        else:
            return "User already exists"
    return render_template('register.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    # Redirect to the Streamlit app for the chatbot
    return redirect("http://localhost:8501")  # Assuming Streamlit runs on port 8501

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    print(f"Received message: {user_message}")  # Debug print
    bot_response = f"Bot: You said '{user_message}'"
    print(f"Sending response: {bot_response}")  # Debug print
    return jsonify({'response': bot_response})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    
    # Open the image using PIL
    image = Image.open(image_file)

    # You can also process the input text if needed
    input_text = request.form.get('input_text', '')

    # Get response from Gemini AI
    response_text = get_gemini_response(input_text, image)

    return jsonify({'response': response_text})

@app.route('/call_ambulance', methods=['POST'])
def call_ambulance():
    # Logic to call the ambulance service can be implemented here
    return jsonify({'message': 'Ambulance is on the way!'})



@app.route('/doctors')
def doctors():
    # Sample list of doctors
    doctors_list = [
        {"name": "Dr. Asha Sharma", "specialization": "Cardiologist", "experience": "10 years", "location": "Delhi", "payment": 500},
        {"name": "Dr. Rajesh Verma", "specialization": "Dermatologist", "experience": "8 years", "location": "Mumbai", "payment": 400},
        {"name": "Dr. Priya Desai", "specialization": "Pediatrician", "experience": "5 years", "location": "Bangalore", "payment": 300},
        {"name": "Dr. Sunil Rao", "specialization": "Orthopedic", "experience": "12 years", "location": "Kolkata", "payment": 600},
        {"name": "Dr. Neha Gupta", "specialization": "General Practitioner", "experience": "6 years", "location": "Chennai", "payment": 350},
        {"name": "Dr. Mohan Nair", "specialization": "Neurologist", "experience": "15 years", "location": "Hyderabad", "payment": 700},
        {"name": "Dr. Anita Menon", "specialization": "Gynecologist", "experience": "7 years", "location": "Ahmedabad", "payment": 450},
        {"name": "Dr. Vikram Singh", "specialization": "ENT Specialist", "experience": "9 years", "location": "Pune", "payment": 400},
        {"name": "Dr. Rhea Kapoor", "specialization": "Endocrinologist", "experience": "11 years", "location": "Jaipur", "payment": 650},
        {"name": "Dr. Arjun Yadav", "specialization": "Urologist", "experience": "14 years", "location": "Lucknow", "payment": 550},
    ]
    return render_template('doctors.html', doctors=doctors_list)

@app.route('/video_call')
def video_call():
    doctor_name = request.args.get('doctor')
    specialization = request.args.get('specialization')
    return render_template('video_call.html', doctor=doctor_name, specialization=specialization)

@app.route('/image_chatbot')
def image_chatbot():
    return redirect("http://localhost:8501")

@app.route('/analyze', methods=['POST'])
def analyze_image():
    input_text = request.form['input']
    uploaded_file = request.files['file']

    if uploaded_file:
        image = Image.open(uploaded_file)
        response_text = get_gemini_response(input_text, image)

        return jsonify({'response': response_text})

    return jsonify({'response': 'No file uploaded.'}), 400

@app.route('/prescription')
def order_medicines():
    return render_template('prescription.html')

@app.route('/book_tests', methods=['GET', 'POST'])
def book_test():
    if request.method == 'POST':
        test_type = request.form['testType']
        date = request.form['date']
        time = request.form['time']
        # Process the booking information as needed
        print(f"Test Type: {test_type}, Date: {date}, Time: {time}")
        return jsonify({'message': 'Form completed. You will be contacted shortly.'})
    return render_template('book_tests.html')  # Replace with your actual template

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Sample patient data (Replace this with actual patient data retrieval logic)
    patient_data = {
        "age": 30,
        "gender": "Male",
        "height": "175 cm",
        "weight": "70 kg",
        "blood_group": "O+",
        "allergies": "None",
        "illness": "Hypertension",
        "ecg": "Normal",
        "ear": "No issues",
        "vision": "20/20",
        "identification_marks": "Birthmark on right arm"
    }
    
    return render_template('profile.html', patient_data=patient_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
