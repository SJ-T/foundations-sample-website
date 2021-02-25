from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
<<<<<<< HEAD
    return '<h1>Hello prpr</h1>' 
=======
    return '<h1>Hello, Class!</h1>'

>>>>>>> upstream/main

 
if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
