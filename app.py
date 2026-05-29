import os
from flask import Flask, render_template, redirect, jsonify,request
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')

def home():
    return render_template('index.html')

@app.route('/ask', methods = ['POST'])
def askchatbot():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "Message not found"}), 404
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents= user_message,
        )

        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)