from flask import Flask, request, jsonify
import pickle
import numpy as np

# Load your AI model
with open("model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

app = Flask(__name__)

# Allow cross-origin requests (if your frontend is hosted elsewhere)
from flask_cors import CORS
CORS(app)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    user_input = data.get("input")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Process input (modify based on your model)
    response = model.predict([user_input])  # Example using a sklearn model

    return jsonify({"response": response[0]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
