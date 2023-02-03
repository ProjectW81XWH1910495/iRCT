from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pandas as pd
import iRCT

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'dat'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        error = ''
        if request.args.get('error', None) != None:
            error = request.args.get('error', None)
        
        return render_template("home.html", error=error)
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect("/")
        f = request.files['file']
        delim = request.form['delim']
        if f and allowed_file(f.filename):
            f.save(f.filename)
            uploaded_file = True
            return redirect(url_for('iRCT_Page', filename=f.filename, uploaded_file=uploaded_file, delim=delim))
        else:
            return redirect("/")

@app.route("/iRCT", methods=['GET', 'POST'])
def iRCT_Page():
    if request.method == 'GET':
        file_uploaded = bool(request.args.get('uploaded_file', None))
        if file_uploaded == True:
            filename = request.args.get('filename', None)
            delim = request.args.get('delim', None)


            df = pd.read_csv(filename, sep=delim)
            listOfColumns = df.columns

            return render_template("iRCT_Page.html", name=filename, columns=listOfColumns, delim=delim)
        else:
            return redirect('/')
    
    if request.method == 'POST':
        treatmentCol = request.form['treat_column']
        outcomeCol = request.form['out_column']
        fileName = request.form['fileName']
        delimiter = request.form['delimiter']

        df = pd.read_csv(fileName, sep=delimiter)
        df.index = range(1, len(df)+1, 1)

        if treatmentCol == outcomeCol:
            errMsg = 'Outcome and Treatment columns cannot be the same.'
            os.remove(fileName)
            return redirect(url_for('home', error=errMsg))
        else:
            myiRCT = iRCT.iRCT(df, treatmentCol, outcomeCol)
            os.remove(fileName)
            return render_template("output.html", result=str(myiRCT.relationVal), outcome=outcomeCol, treatment=treatmentCol)

if __name__ == "__main__":
    app.run(debug=True)


    #TODO
    # Add function to make sure delimiter is correct for that file
    # Make all pages more visually appealing
    # Add Text to pages describing how different features work and what input types should look like
    # Make sure file uploaded is deleted no matter what
    # Add feature to choose between all three existing functions, and if a function doesn't work with that datset delete the file and return to the homepage saying there was an error loading that function.