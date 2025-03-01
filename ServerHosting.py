import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import random
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Store models in global variables but don't load them until needed
model = None
nn_model = None
df = None
transitions_df = None

# Session memory
session_memory = []

def load_models():
    """Lazy load models when needed"""
    global model, nn_model, df, transitions_df
    
    if model is None:
        print("Loading SBERT model...")
        model = joblib.load("sbert_model.pkl")  # SBERT model
    
    if nn_model is None:
        print("Loading Nearest Neighbors model...")
        nn_model = joblib.load("nn_model.pkl")  # Nearest Neighbors model
    
    if df is None:
        print("Loading chatbot data...")
        df = joblib.load("chatbot_data.pkl")  # Chatbot responses
    
    if transitions_df is None:
        print("Loading word transitions...")
        transitions_df = joblib.load("word_transitions.pkl")  # Word transitions

    print("Models are loaded!")

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
    # Lazy load models if not loaded yet
    load_models()
    
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

# Serve static website (index.html)
@app.route("/")
def home():
    """Serves the static index.html page"""
    return send_from_directory('Website', 'index.html')

if __name__ == "__main__":
    # Use the port provided by Render or default to 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)


#cd C:\Users\tywfr\OneDrive\Documents\GitHub\AthenaEdTech
#python ServerHosting.py