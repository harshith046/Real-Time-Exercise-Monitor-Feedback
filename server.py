from flask import Flask, request, jsonify
import subprocess
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

selected_exercise = None

@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    global selected_exercise
    data = request.get_json()
    if 'exercise_type' in data:
        selected_exercise = data['exercise_type']
        return jsonify({"message": f"Exercise set to {selected_exercise}"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route('/start_exercise', methods=['GET'])
def start_exercise():
    global selected_exercise
    if not selected_exercise:
        return jsonify({"error": "No exercise selected."}), 400
    try:
        print(f"Starting exercise: {selected_exercise}")
        # Run main.py synchronously so that it completes and writes exercise_result.json.
        result = subprocess.run(['python', 'main.py', selected_exercise], capture_output=True, text=True)
        # Read the final result from exercise_result.json.
        if os.path.exists("exercise_result.json"):
            with open("exercise_result.json", "r") as f:
                result_data = json.load(f)
            return jsonify(result_data), 200
        else:
            return jsonify({"error": "Result file not found."}), 500
    except Exception as e:
        print(f"Error starting exercise: {e}")
        return jsonify({"error": "Failed to start exercise."}), 500

if __name__ == '__main__':
    app.run(debug=True)
