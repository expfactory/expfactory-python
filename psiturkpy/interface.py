from psiturkpy.experiment import validate, load_experiment, get_experiments
from psiturkpy.battery import generate, generate_config
from psiturkpy.utils import copy_directory
from flask import Flask, render_template, request
from werkzeug import secure_filename
from git import Repo
import tempfile
import shutil
import random
import os

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','gif'])
    
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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
    tmpdir = tempfile.mkdtemp()
    return render_template('index.html',tmpdir=tmpdir)

@app.route('/validate',methods=['POST'])
def validate():
    logo = None
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field!="tmpdir":
                fields[field] = value
            else:
                tmpdir = value

        # Parse the database url for the config
        fields["database_url"] = "%s://%s:%s@%s/%s"  %(fields["dbtype"],
                                                     fields["dbusername"],
                                                     fields["dbpassword"],
                                                     fields["dbhost"],
                                                     fields["dbtable"])

        # Download battery and experiment repos
        erepo = download_repo("experiments","%s/experiments/" %tmpdir)
        brepo = download_repo("battery","%s/battery/" %tmpdir)

        # Copy the custom logo
        if "file" in request.files and allowed_file(request.files["file"]):
            logo = secure_filename(request.files["file"])
            shutil.copy(logo,"%s/battery/img/logo.png" %(tmpdir))
            #logo = allowed_files(request.files['file'])
    
        # Generate battery folder with config file with parameters
        generate_config("%s/battery" %(tmpdir),fields)

        # Get valid experiments
        #TODO: in future should let user select based on cognitive atlas
        valid_experiments = get_experiments("%s/experiments/" %(tmpdir),load=True)

        return render_template('experiments.html',
                                experiments=str(valid_experiments),
                                this_many=len(valid_experiments),
                                tmpdir=tmpdir)
    return render_template('index.html')

@app.route('/select',methods=['POST'])
def select():
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field!="tmpdir":
                fields[field] = value
            else:
                tmpdir = value

        # Retrieve experiment folders 
        valid_experiments = get_experiments("%s/experiments" %(tmpdir),load=True)
        experiments =  [x[0]["tag"] for x in valid_experiments]
        selected_experiments = [x for x in fields.values() if x in experiments]
        experiment_folders = ["%s/experiments/%s" %(tmpdir,x) for x in selected_experiments]

        # Add to the battery, clean up old folder
        generate("%s/battery"%(tmpdir),"%s/psiturk-battery" %tmpdir,experiments=experiment_folders)
        shutil.rmtree("%s/experiments"%(tmpdir))
        shutil.rmtree("%s/battery"%(tmpdir))
        battery_dest = "%s/psiturk-battery" %(tmpdir)

        return render_template('complete.html',battery_dest=battery_dest)
    return render_template('index.html')


def download_repo(repo_type,destination):
    if repo_type == "experiments":
        return Repo.clone_from("https://github.com/psiturk/psiturk-experiments", destination)
    elif repo_type == "battery":
        return Repo.clone_from("https://github.com/psiturk/psiturk-battery", destination)

# This is how the command line version will run
def main():
    print "Time for Psiturkpy!"
    app.run(host="0.0.0.0",debug=True)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
