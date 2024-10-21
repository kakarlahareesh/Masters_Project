from flask import Flask, render_template, jsonify
import requests
import time
import json

app = Flask(__name__)

# API Endpoints
APIS = [
    'https://y18va6f6rc.execute-api.us-east-1.amazonaws.com/Server1',
    'https://unbf0byjdc.execute-api.us-east-2.amazonaws.com/Server2'
]

# Initialize the API index
api_index = 0

def fetch_patient_data():
    global api_index
    error_time = 0
    # Try each API endpoint in round-robin fashion
    for _ in range(len(APIS)):
        api = APIS[api_index]
        try:
            response = requests.get(api)
            response.raise_for_status()
            data = response.json()
            body = data.get('body')
            if body:
                patient_data = json.loads(body)  # Use json.loads to parse JSON string safely
                # Update the index to the next API for subsequent calls
                api_index = (api_index + 1) % len(APIS)
                return patient_data, api, error_time  # Return patient data, API URL, and time taken
            else:
                patient_data = {}
                return patient_data, api, error_time
        except requests.RequestException:
            error_time += 3  # Accumulate error time in seconds
            # Move to the next API in the list
            api_index = (api_index + 1) % len(APIS)
        except Exception as e:
            print(f"Error processing API response: {e}")
            # Update the index to the next API even if an exception occurs
            api_index = (api_index + 1) % len(APIS)
            return None, None, error_time
    
    # Return None if all APIs fail
    return None, None, error_time  

@app.route('/')
def index():
    return render_template('fetch_patient.html')

@app.route('/fetch')
def fetch_patient():
    start_time = time.time()
    data, api_used, error_time = fetch_patient_data()
    total_time = round(time.time() - start_time + error_time, 2)  # Ensure total_time is a float

    if data:
        return render_template('output.html', patient_data=data, api_details=api_used, total_time=total_time)
    else:
        return render_template('output.html', error_message="Failed to fetch data from all endpoints", total_time=total_time)

if __name__ == '__main__':
    app.run(debug=True)
