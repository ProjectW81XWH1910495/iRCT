from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template("home.html")
    else:
        treatmentCol = request.form['Treatment Column']
        outcomeCol = request.form['Outcome Column']

if __name__ == "__main__":
    app.run(debug=True)