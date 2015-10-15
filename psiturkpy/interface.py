from flask import Flask, render_template, request
import random

app = Flask(__name__)

"""
Get value from a form field

"""
def get_field(request,fields,value):
    if value in request.form.values():
        fields[value] = request.form[value]
    return fields

"""
Main function for starting interface to generate a battery
"""
@app.route('/')
def start():
    return render_template('index.html')

@app.route('/validate',methods=['POST'])
def validate():
    logo = None
    print request.method
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            fields[field] = value 
        if "wizard-picture" in request.files:
            logo = request.files['wizard-picture']
        return render_template('index.html',logo=logo,fields=fields)
    return render_template('index.html',logo=logo)

# Variable selection
@app.route('/<font>/<color1>/<color2>/<hidden>')
def update_logo(font,color1,color2,hidden):
    response = update_graphic(font,"#%s" %color1,"#%s" %color2,hidden)
    return response

# This is how the command line version will run
def main():
    #import webbrowser, random, threading
    #port = 5000 + random.randint(0, 999)
    print "Time for Psiturkpy!"
    #url = "http://127.0.0.1:{0}".format(port)
    #threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run(host="0.0.0.0",debug=True)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
