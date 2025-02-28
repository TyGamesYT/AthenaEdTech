print("Starting Up")
from flask import Flask, request, jsonify
import joblib
import random
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Flask
from flask_cors import CORS
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load trained components
print("Loading chatbot models...")
model = joblib.load("sbert_model.pkl")  # SBERT model
nn_model = joblib.load("nn_model.pkl")  # Nearest Neighbors model
df = joblib.load("chatbot_data.pkl")  # Chatbot responses
transitions_df = joblib.load("word_transitions.pkl")  # Word transitions

print("Chatbot Ready!")

session_memory = []

def add_to_memory(user_input, bot_response):
    """Stores last 3 user-bot interactions"""
    if len(session_memory) >= 6:
        session_memory.pop(0)
    session_memory.append({"user": user_input, "bot": bot_response})

def generate_sentence(start_word, max_length=10):
    """Generates a response based on word transitions"""
    sentence = [start_word]
    
    for _ in range(max_length - 2):
        possible_next_words = transitions_df[transitions_df["word1"] == sentence[-1]]
        
        if possible_next_words.empty:
            break
        
        next_row = possible_next_words.sample(weights=possible_next_words["count"], n=1)
        next_word1 = next_row["word2"].values[0]
        next_word2 = next_row["word3"].values[0]
        
        sentence.append(next_word1)
        sentence.append(next_word2)

    return " ".join(sentence[:max_length])

def get_response(user_input):
    context = ""
    for entry in session_memory:
        context += f"You: {entry['user']}\nBot: {entry['bot']}\n"
    context += f"You: {user_input}\n"

    user_input_vec = model.encode([context])
    
    distances, idx = nn_model.kneighbors(user_input_vec)
    best_match_idx = idx[0][0]
    similarity_score = 1 / (1 + distances[0][0])

    similarity_threshold = 0.75  

    if similarity_score < similarity_threshold:
        with open('UnknownQuestions.txt', 'a') as file:
            file.write(user_input + "\n")

        words = user_input.split()
        start_word = random.choice(words) if words else "the"
        return generate_sentence(start_word)
    
    response = df["response"].iloc[best_match_idx]
    add_to_memory(user_input, response)
    return response

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """Handles chatbot requests from the website"""
    data = request.get_json()
    user_input = data.get("message", "")
    
    print(user_input)
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    response = get_response(user_input)
    return jsonify({"answer": response})
    print(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

#cd C:\Users\tywfr\OneDrive\Documents\GitHub\AthenaEdTech
#python ServerHosting.py