import os
import torch
from flask import Flask, render_template, jsonify, request
from transformers import AutoModelForCausalLM, AutoTokenizer
import psycopg2

# ye mene database k lie code dea hai isme sirf databse dala hua hai
DB_CONFIG = {
    "dbname": "chatbot-db",
    "user" : "postgres",
    "password" : "8288",
    "host": "localhost"
}
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM chatdata")
    print("Database connected! Table count:", cur.fetchone()[0])
    cur.close()
    conn.close()
except Exception as e:
    print("Connection Failed:", e)

def save_db(role, content):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO chatdata (role, content) VALUES(%s, %s)", (role, content))
        print("Saved {role} message to DB")
    except Exception as e:
        print(f"Error : {e}")


app = Flask(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    device_map  ="cpu"
)


print('Model Loaded successfully')
chat_history=[]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods= ['POST'])
def askchatbot():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "Message not found"}), 404
    
    try:
        save_db("user", user_message)
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        prompt = tokenizer.apply_chat_template(chat_history, tokenize= False, add_generation_prompt= True)
        inputs = tokenizer([prompt], return_tensors="pt").to(model.device)

        outputs = model.generate(**inputs, max_new_tokens=250, do_sample=True, temperature = 0.7)
        full_response = tokenizer.decode(outputs[0], skip_special_tokens = True)

        bot_reply = full_response.split("<|assistant|>")[-1].strip()
 
        save_db("assistant", bot_reply)
        
        chat_history.append({
            "role" : "assistant",
            "content": bot_reply
        })

        return jsonify({"response": bot_reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/history', methods=['GET'])

def get_history():
        try:             
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT role, content FROM chatdata ORDER BY created_at ASC")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            history = [{"role": row[0], "text": row[1]} for row in rows]
            return jsonify({"history": history})
        except Exception as e:
            return jsonify({"history": [], "error": str(e)})

@app.route('/clear', methods=['POST'])
def clear_history():
    chat_history.clear()
    return jsonify({"message": "History Cleared"})

save_db("system", "Test message: Database is working!")
if __name__ == '__main__':
    app.run(debug= True)