from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/',methods=['GET'])
def index():
    return {'RESPONSE':"HELLO WORLD"}



@app.route('/prompt',methods=['POST'])
def test():
    data = request.get_json()  # Get JSON data from the request
    print(data)  # Print the received data
    return jsonify(data)  # Respond back with the received data

if __name__ == '__main__':
    app.run(debug=True)
