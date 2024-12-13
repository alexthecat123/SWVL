from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/test-function")
def test_function():
        string = request.args.get('string')
        return {"result": "The string you gave me was: " + string}




if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="5000")