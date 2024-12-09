import mysql.connector
import json
import os

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'unique chatbot' 
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

query = "SELECT question, answer FROM intent" 
cursor.execute(query)

intents = []

def find_intent_by_response(intents, answer):
    for intent in intents:
        if intent['responses'][0] == answer: 
            return intent
    return None

for (question, answer) in cursor:
    
    existing_intent = find_intent_by_response(intents, answer)
    
    if existing_intent:
        
        existing_intent['patterns'].append(question)
    else:
        
        new_intent = { 
            'patterns': [question],
            'responses': [answer]
        }
        intents.append(new_intent)

cursor.close()
conn.close()

intents_json = {
    'intents': intents
}

intents_file_path = os.path.join('C:\\xammpp\\htdocs\\UniQue-ChatBot', 'intents.json')

json_data = json.dumps(intents_json, indent=4)
with open(intents_file_path, 'w') as json_file:
    json_file.write(json_data)

print("Intents are Successfully Updated.")


