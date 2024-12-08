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

app = Flask(__name__)
CORS(app)

with open('intents.json') as file:
    intents = json.load(file)

model = SentenceTransformer('all-Mpnet-base-v2')

patterns = [pattern for intent in intents['intents'] for pattern in intent['patterns']]
pattern_embeddings = model.encode(patterns, convert_to_tensor=True)

def predict(user_input):

    if profanity.contains_profanity(user_input):
        return "Please be respectful. Let's keep our conversation friendly. "
    
    if re.match(r'^[^a-zA-Z]*$', user_input) or len(set(user_input)) <= 3:
        return "I’m having trouble understanding that. Can you give me a bit more detail about what you're asking?"

    # Fuzzy matching check
    best_match_score_fuzzy = 0
    best_match_idx_fuzzy = -1
    for i, pattern in enumerate(patterns):
        score = fuzz.ratio(user_input.lower(), pattern.lower())
        if score > best_match_score_fuzzy:
            best_match_score_fuzzy = score
            best_match_idx_fuzzy = i

    # Sentence transformer cosine similarity check
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(user_embedding, pattern_embeddings)[0]
    best_match_idx_cosine = np.argmax(cosine_scores)
    best_match_score_cosine = cosine_scores[best_match_idx_cosine]

    # Combine both fuzzy matching and cosine similarity results
    if best_match_score_fuzzy > 65 or best_match_score_cosine > 0.65: 
        best_match_idx = best_match_idx_fuzzy if best_match_score_fuzzy > best_match_score_cosine else best_match_idx_cosine
        for intent in intents['intents']:
            if patterns[best_match_idx] in intent['patterns']:
                return random.choice(intent['responses'])

    return """My current version does not have the specific information for your query. For further assistance, you can contact the specific concerned offices:\n\n<b>Registrar's Office:</b>\nTelephone: (043) 416-0350 local 214\nEmail: registrar.nasugbu@g.batstate-u.edu.ph
\n<b>Testing and Admission Office:</b>\nTelephone: 416-0350 local 216\nEmail: tao.nasugbu@g.batstate-u.edu.ph\nOfficial Facebook Page: https://fb.com/TestingAndAdmissionOffice"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    response = predict(message)
    return jsonify({"response": response})
