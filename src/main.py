from flask import Flask, render_template, request, url_for, redirect , flash , session , abort , jsonify
from datetime import datetime
import os
import time
from modules.agent import InfauxAgent

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure  folder exists

def save_image(uploaded_image):
    filename = os.path.join(UPLOAD_FOLDER, uploaded_image.filename)
    uploaded_image.save(filename)
    return filename

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/user_query", methods=['POST'])
def user_query():
    agent = InfauxAgent()

    try:
        text_message = request.form.get("user_text_input", "").strip() 
        uploaded_image = request.files.get("uploaded_image")  
        is_uploaded_image_exists = uploaded_image and uploaded_image.filename != "" 
        # print("Text:", text_message)
        # print("Uploaded Image:", uploaded_image.filename if is_uploaded_image_exists else "No Image Uploaded")
        if text_message and is_uploaded_image_exists:
            filename = save_image(uploaded_image)
            # print("User Entered Text And Uploaded Image") Format 1
            return jsonify({"success": "User Entered Text And Uploaded Image",
                            "response" : "User Entered Text And Uploaded Image",
                            "uploaded_image_url" : filename
                            }), 200
        
        if text_message and not is_uploaded_image_exists:
            # print("User Entered Text But Did Not Upload Image") Format 2
            response = agent.respond(text_message)
            return jsonify({"success" :  "User Entered Text But Did Not Upload Image",
                            "response" : response
                            }), 200
        
        if not text_message and is_uploaded_image_exists:
            # print("User Did Not Enter Text But Uploaded Image") Format 3
            filename = save_image(uploaded_image)
            return jsonify({"success":  "User Did Not Enter Text But Uploaded Image",
                            "response": "User Did Not Enter Text But Uploaded Image",
                            "uploaded_image" : filename
                            }), 200
        
        if not text_message and not is_uploaded_image_exists:
            print("No Text Input and No File Uploaded")
            return jsonify({"error": "No Text Input and No File Uploaded"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)