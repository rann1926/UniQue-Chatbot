import os
import json
import random
import re
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from better_profanity import profanity
from fuzzywuzzy import fuzz
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

with open('intents.json') as file:
    intents = json.load(file)

model = SentenceTransformer('all-Mpnet-base-v2')

patterns = [pattern for intent in intents['intents'] for pattern in intent['patterns']]
pattern_embeddings = model.encode(patterns, convert_to_tensor=True)

# Prediction function using Sentence Transformers
def predict(user_input):

    if profanity.contains_profanity(user_input):
        return "Please be respectful. Let's keep our conversation friendly. "

    user_embedding = model.encode(user_input, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(user_embedding, pattern_embeddings)[0]
    best_match_idx = np.argmax(cosine_scores)
    best_match_score = cosine_scores[best_match_idx]

    if best_match_score > 0.7:  # Adjust threshold as needed
        # Find the corresponding intent
        for intent in intents['intents']:
            if patterns[best_match_idx] in intent['patterns']:
                return random.choice(intent['responses'])

    if re.match(r'^[^a-zA-Z]*$', user_input) or len(set(user_input)) <= 3:
        return "I’m having trouble understanding that. Can you give me a bit more detail about what you're asking?"

    return """My current version does not have the specific information for your query. For further assistance, you can contact the specific concerned offices:\n\n<b>Registrar's Office:</b>\nTelephone: (043) 416-0350 local 214\nEmail: registrar.nasugbu@g.batstate-u.edu.ph
\n<b>Testing and Admission Office:</b>\nTelephone: 416-0350 local 216\nEmail: tao.nasugbu@g.batstate-u.edu.ph\nOfficial Facebook Page: https://fb.com/TestingAndAdmissionOffice"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    response = predict(message)
    return jsonify({"response": response})

@app.route('/update-intents', methods=['GET', 'POST'])
def update_intents():
    try:
        # Run the fetch_json.py script
        result = subprocess.run(['python3', 'fetch_json.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"message": "Intents updated successfully!"}), 200
        else:
            return jsonify({"error": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500