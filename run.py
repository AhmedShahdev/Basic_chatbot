import os
import torch
from flask import Flask, render_template, jsonify, request
from transformers import AutoModelForCausalLM, AutoTokenizer



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
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        prompt = tokenizer.apply_chat_template(chat_history, tokenize= False, add_generation_prompt= True)
        inputs = tokenizer([prompt], return_tensors="pt").to(model.device)

        outputs = model.generate(**inputs, max_new_tokens=250, do_sample=True, temperature = 0.7)
        full_response = tokenizer.decode(outputs[0], skip_special_tokens = True)

        bot_reply = full_response.split("<|assistant|>")[-1].strip()


        chat_history.append({
            "role" : "assistant",
            "content": bot_reply
        })

        return jsonify({"response": bot_reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/history', methods=['GET'])
def get_history():
    formatted_history = []
    for msg in chat_history:
        formatted_history.append({
            "role": msg["role"],
            "text": msg["content"]
        })
    return jsonify({"history": formatted_history})
    

@app.route('/clear', methods=['POST'])
def clear_history():
    chat_history.clear()
    return jsonify({"message": "History Cleared"})


if __name__ == '__main__':
    app.run(debug= True)