import os
from flask import Flask, render_template, redirect, jsonify,request
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chat_history = []
@app.route('/')

def home():
    return render_template('index.html')

@app.route('/ask', methods = ['POST'])
def askchatbot():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "Message not found"}), 404
    
    try:
        chat_history.append({
            "role": "user",
            "parts" : [{"text": user_message}]
        })
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents= chat_history,
        )

        bot_reply = response.text

        chat_history.append({
            "role" : "model",
            "parts" : [{"text" : bot_reply}]
        })

        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/clear', methods = ['POST'])
def clear_history():
    chat_history.clear()
    return jsonify({"message": "History cleared"})


if __name__ == '__main__':
    app.run(debug=True)