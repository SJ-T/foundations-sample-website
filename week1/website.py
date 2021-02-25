from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/community')
def community():
    return render_template('community.html', page_title="Community")


@app.route('/studyprogram')
def studyprogram():
    return render_template('studyprogram.html', page_title="Study Program")

# add additonal pages here using a similar format as above


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
