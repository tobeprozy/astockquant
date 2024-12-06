from flask import Flask, jsonify
from data_fetcher.static_data import fetch_static_data
from data_fetcher.real_time_data import fetch_real_time_data

app = Flask(__name__)

@app.route('/api/static-data', methods=['GET'])
def get_static_data():
    data = fetch_static_data()
    return jsonify(data)

@app.route('/api/real-time-data', methods=['GET'])
def get_real_time_data():
    data = fetch_real_time_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
