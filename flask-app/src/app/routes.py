from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask App!"

@app.route('/api')
def api():
    return {"message": "This is the API endpoint."}