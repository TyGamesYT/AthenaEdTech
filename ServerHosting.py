import os
import random
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Lazy-loaded global variables
sbert_model = None
nn_model = None
chatbot_data = None
transitions_df = None
session_memory = []  # Stores last 3 user-bot interactions

def load_models():
    """Loads models only when needed to reduce memory usage."""
    global sbert_model, nn_model, chatbot_data, transitions_df

    if sbert_model is None:
        print("Loading SBERT model...")
        sbert_model = joblib.load("sbert_model.pkl")  # Sentence-BERT model

    if nn_model is None:
        print("Loading Nearest Neighbors model...")
        nn_model = joblib.load("nn_model.pkl")  # NN model for similarity search

    if chatbot_data is None:
        print("Loading chatbot responses...")
        chatbot_data = joblib.load("chatbot_data.pkl")  # Predefined responses

    if transitions_df is None:
        print("Loading word transitions...")
        transitions_df = joblib.load("word_transitions.pkl")  # Word transition data

def add_to_memory(user_input, bot_response):
    """Stores last 3 user-bot interactions to maintain conversation context."""
    if len(session_memory) >= 6:
        session_memory.pop(0)
    session_memory.append({"user": user_input, "bot": bot_response})

def generate_sentence(start_word, max_length=10):
    """Generates a response based on word transitions when no good match is found."""
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
    """Finds the best chatbot response using SBERT + Nearest Neighbors."""
    load_models()  # Ensure models are loaded before processing

    # Build conversation context
    context = ""
    for entry in session_memory:
        context += f"You: {entry['user']}\nBot: {entry['bot']}\n"
    context += f"You: {user_input}\n"

    user_input_vec = sbert_model.encode([context])

    distances, idx = nn_model.kneighbors(user_input_vec)
    best_match_idx = idx[0][0]
    similarity_score = 1 / (1 + distances[0][0])

    similarity_threshold = 0.75  # Minimum similarity for a valid response

    if similarity_score < similarity_threshold:
        # Log unknown questions for later improvement
        with open("UnknownQuestions.txt", "a") as file:
            file.write(user_input + "\n")

        # Generate a random response if no close match is found
        words = user_input.split()
        start_word = random.choice(words) if words else "the"
        return generate_sentence(start_word)

    response = chatbot_data["response"].iloc[best_match_idx]
    add_to_memory(user_input, response)
    return response

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """Handles chatbot API requests."""
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = get_response(user_input)
    return jsonify({"answer": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT variable
    print(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)


#cd C:\Users\tywfr\OneDrive\Documents\GitHub\AthenaEdTech
#python ServerHosting.py