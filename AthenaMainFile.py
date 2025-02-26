import joblib
import pandas as pd
import random

# Load trained components
print("Loading chatbot models...")
model = joblib.load("sbert_model.pkl")
nn_model = joblib.load("nn_model.pkl")
df = joblib.load("chatbot_data.pkl")
transitions_df = joblib.load("word_transitions.pkl")

print("Chatbot Ready!")

session_memory = []

# Store context for conversation (e.g., last 2 user inputs and responses)
def add_to_memory(user_input, bot_response):
    """Add recent user input and bot response to session memory"""
    if len(session_memory) >= 6:  # Limit the memory to 3 exchanges (6 turns)
        session_memory.pop(0)  # Remove the oldest entry
    session_memory.append({"user": user_input, "bot": bot_response})

def generate_sentence(start_word, max_length=10):
    """Generates a response using **three-word sequences** for better fluency"""
    sentence = [start_word]
    
    for _ in range(max_length - 2):  # Adjust for three-word sequences
        # Find possible next word pairs in the dataset
        possible_next_words = transitions_df[
            (transitions_df["word1"] == sentence[-1])
        ]
        
        if possible_next_words.empty:
            break  # Stop if no known next words
        
        # Choose the most frequent word pair
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
    """Finds the best response or generates one if no match is found"""
    distances, idx = nn_model.kneighbors(user_input_vec)
    best_match_idx = idx[0][0]
    similarity_score = 1 / (1 + distances[0][0])

    similarity_threshold = 0.75  

    if similarity_score < similarity_threshold:
        with open('UnknownQuestions.txt', 'a') as file:
            file.write(user_input + "\n")

        # Pick a random word from user input to start generation
        words = user_input.split()
        start_word = random.choice(words) if words else "the"
        return generate_sentence(start_word)
    
    response = df["response"].iloc[best_match_idx]
    add_to_memory(user_input, response)
    return response

print("\nChatbot is running. Type 'exit' to stop.\n")

# Main interaction loop
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Goodbye! Have a great day!")
        break
    response = get_response(user_input)
    print("Bot:", response)
