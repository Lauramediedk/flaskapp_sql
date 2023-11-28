from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)

#Routes
@app.route("/")
def index():
    return render_template("index.html")

#app run
if __name__=="__main__":
    app.run(host='0.0.0.0', port=80, debug=True)