from expfactory.vm import custom_battery_download, add_custom_logo, generate_database_url, \
     prepare_vm, specify_experiments, download_repo
from expfactory.experiment import validate, load_experiment, get_experiments
from expfactory.battery import generate, generate_config
from flask import Flask, render_template, request
from expfactory.utils import copy_directory
from werkzeug import secure_filename
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
# Step 0: User is presented with base interface
@app.route('/')
def start():
    tmpdir = tempfile.mkdtemp()
    return render_template('index.html',tmpdir=tmpdir)


# STEP 1: Validation of user input for battery
@app.route('/validate',methods=['POST'])
def validate():
    logo = None
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field == "tmpdir":
                tmpdir = value
            elif field == "dbsetupchoice":
                dbsetupchoice = value
            else:
                fields[field] = value

        # DATABASE SETUP ###################################################
        # If the user wants to generate a custom database:
        if dbsetupchoice == "manual":

            # Generate a database url from the inputs
            fields["database_url"] =  generate_database_url(dbtype=fields["dbtype"],
                                                 username=fields["dbusername"],
                                                 password=fields["dbpassword"],
                                                 host=fields["dbhost"],
                                                 table=fields["dbtable"]) 
        else:
            # If generating a folder, use sqlite3
            if fields["deploychoice"] == "folder":
                fields["database_url"] = generate_database_url(template="sqlite3")       
            # Otherwise, use postgres
            else: 
                fields["database_url"] = generate_database_url(template="mysql")       
        
        # LOCAL FOLDER #####################################################
        if fields["deploychoice"] == "folder":

            # Prepare temp folder with battery and experiments
            custom_battery_download(tmpdir=tmpdir)

            # Copy the custom logo
            if "file" in request.files and allowed_file(request.files["file"]):
                logo = secure_filename(request.files["file"])
                add_custom_logo(battery_repo="%s/battery" %(tmpdir),logo=logo)
    
            # Generate battery folder with config file with parameters
            generate_config("%s/battery" %(tmpdir),fields)

        else: 
            prepare_vm(battery_dest=tmpdir,fields=fields,vm_type=fields["deploychoice"])
            download_repo("experiments","%s/experiments/" %(tmpdir))

        # Get valid experiments to present to user
        valid_experiments = get_experiments("%s/experiments/" %(tmpdir),load=True)

        return render_template('experiments.html',
                                experiments=str(valid_experiments),
                                this_many=len(valid_experiments),
                                tmpdir=tmpdir,
                                deploychoice=fields["deploychoice"])

    return render_template('index.html')

# STEP 2: User must select experiments
@app.route('/select',methods=['POST'])
def select():
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field == "tmpdir":
                tmpdir = value
            elif field == "deploychoice":
                deploychoice = value
            else:
                fields[field] = value

        # Retrieve experiment folders 
        valid_experiments = get_experiments("%s/experiments" %(tmpdir),load=True)
        experiments =  [x[0]["tag"] for x in valid_experiments]
        selected_experiments = [x for x in fields.values() if x in experiments]
        experiment_folders = ["%s/experiments/%s" %(tmpdir,x) for x in selected_experiments]

        # Option 1: A folder on the local machine
        if deploychoice == "folder":

            # Add to the battery
            generate(battery_dest="%s/expfactory-battery"%tmpdir,
                     battery_repo="%s/battery"%tmpdir,
                     experiments=experiment_folders,
                     make_config=False)

            battery_dest = "%s/expfactory-battery" %(tmpdir)

        # Option 2 or 3: Virtual machine (vagrant) or cloud (aws)
        else:
            specify_experiments(battery_dest=tmpdir,experiments=selected_experiments)
            battery_dest = tmpdir 

        # Clean up
        clean_up("%s/experiments"%(tmpdir))
        clean_up("%s/battery"%(tmpdir))
        clean_up("%s/vm"%(tmpdir))        

        return render_template('complete.html',battery_dest=battery_dest)
    return render_template('index.html')


def clean_up(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)


# This is how the command line version will run
def main():
    print "Start up the Experiment Factory!"
    print "Nobody ever comes in... nobody ever comes out..."
    app.run(host="0.0.0.0",debug=True)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
