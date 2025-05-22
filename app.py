from flask import Flask, render_template, request, jsonify
import signal
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv('CLAUDE_API_KEY')
if not api_key:
    raise ValueError("Claude API key not found in environment variables")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_here')

client = anthropic.Anthropic(api_key=api_key)

def get_air_quality_prediction(location, date):
    try:
        prompt = f"""Based on historical data and current conditions, predict the air quality for {location} on {date}.
        Consider factors like:
        - PM2.5 levels
        - Ozone levels
        - Nitrogen dioxide
        - Sulfur dioxide
        - Carbon monoxide
        
        Provide a detailed prediction with:
        1. Overall air quality index (0-500)
        2. Main pollutants
        3. Health recommendations
        4. Confidence level of the prediction
        
        Format the response in a clear, structured way."""
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating prediction: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    location = request.form.get('location')
    date = request.form.get('date')
    
    if not location or not date:
        return jsonify({'error': 'Location and date are required'}), 400
    
    prediction = get_air_quality_prediction(location, date)
    return jsonify({'prediction': prediction})

@app.route('/test-api-key', methods=['GET'])
def test_api_key():
    try:
        # Check if API key exists and is not empty
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key is not set'
            }), 500
        
        # Try to make a minimal API call to verify the key
        test_response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            temperature=0,
            messages=[
                {"role": "user", "content": "Test connection"}
            ]
        )
        
        return jsonify({
            'status': 'success',
            'message': 'API key is valid and working',
            'api_key_length': len(api_key)  # Only return the length for security
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API key test failed: {str(e)}'
        }), 500

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.run(debug=True, port=5002) 