from expfactory.vm import custom_battery_download, add_custom_logo, generate_database_url, \
     prepare_vm, specify_experiments
from expfactory.experiment import validate, load_experiment, get_experiments, make_lookup
from expfactory.utils import copy_directory, get_installdir, sub_template
from expfactory.battery import generate, generate_config
from flask import Flask, render_template, request
from flask_restful import Resource, Api
from werkzeug import secure_filename
import webbrowser
import tempfile
import shutil
import random
import os

# SERVER CONFIGURATION ##############################################
class EFServer(Flask):

    def __init__(self, *args, **kwargs):
            super(EFServer, self).__init__(*args, **kwargs)

            # download repo on start of application
            self.tmpdir = tempfile.mkdtemp()
            custom_battery_download(tmpdir=self.tmpdir)
            self.experiments = get_experiments("%s/experiments" %self.tmpdir,load=True,warning=False)
            self.experiment_lookup = make_lookup(self.experiments,"exp_id")

# API VIEWS #########################################################
class apiExperiments(Resource):
    '''apiExperiments
    Main view for REST API to display all available experiments
    '''
    def get(self):
        experiment_json = app.experiments
        return experiment_json

class apiExperimentSingle(Resource):
    '''apiExperimentSingle
    return complete meta data for specific experiment
    :param exp_id: exp_id for experiment to preview
    '''
    def get(self, exp_id):
        return {exp_id: app.experiment_lookup[exp_id]}

app = EFServer(__name__)
api = Api(app)    
api.add_resource(apiExperiments,'/experiments')
api.add_resource(apiExperimentSingle,'/experiments/<string:exp_id>')


# WEB INTERFACE VIEWS ##############################################

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','gif'])
    
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def get_field(request,fields,value):
    """
    Get value from a form field

    """

    if value in request.form.values():
        fields[value] = request.form[value]
    return fields

# Home screen for user to select what they want
@app.route('/')
def home():
    return render_template('index.html')


# INTERACTIVE BATTERY GENERATION ####################################################
# Step 0: User is presented with base interface
@app.route('/battery')
def battery():
    return render_template('battery.html')

# STEP 1: Validation of user input for battery
@app.route('/battery/validate',methods=['POST'])
def validate():
    logo = None
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.items():
            if field == "dbsetupchoice":
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

            # Copy the custom logo
            if "file" in request.files and allowed_file(request.files["file"]):
                logo = secure_filename(request.files["file"])
                add_custom_logo(battery_repo="%s/battery" %(app.tmpdir),logo=logo)
    
            # Generate battery folder with config file with parameters
            generate_config("%s/battery" %(app.tmpdir),fields)

        else: 
            prepare_vm(battery_dest=app.tmpdir,fields=fields,vm_type=fields["deploychoice"])

        # Get valid experiments to present to user
        valid_experiments = [{"exp_id":e[0]["exp_id"],"name":e[0]["name"]} for e in app.experiments]

        return render_template('experiments.html',
                                experiments=str(valid_experiments),
                                this_many=len(valid_experiments),
                                deploychoice=fields["deploychoice"])

    return render_template('battery.html')

# STEP 2: User must select experiments
@app.route('/battery/select',methods=['POST'])
def select():
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.items():
            if field == "deploychoice":
                deploychoice = value
            else:
                fields[field] = value

        # Retrieve experiment folders 
        valid_experiments = app.experiments
        experiments =  [x[0]["exp_id"] for x in valid_experiments]
        selected_experiments = [x for x in fields.values() if x in experiments]
        experiment_folders = ["%s/experiments/%s" %(app.tmpdir,x) for x in selected_experiments]

        # Option 1: A folder on the local machine
        if deploychoice == "folder":

            # Add to the battery
            generate(battery_dest="%s/expfactory-battery"%app.tmpdir,
                     battery_repo="%s/battery"%app.tmpdir,
                     experiment_repo="%s/experiments"%app.tmpdir,
                     experiments=experiment_folders,
                     make_config=False,
                     warning=False)

            battery_dest = "%s/expfactory-battery" %(app.tmpdir)

        # Option 2 or 3: Virtual machine (vagrant) or cloud (aws)
        else:
            specify_experiments(battery_dest=app.tmpdir,experiments=selected_experiments)
            battery_dest = app.tmpdir 

        # Clean up
        clean_up("%s/experiments"%(app.tmpdir))
        clean_up("%s/battery"%(app.tmpdir))
        clean_up("%s/vm"%(app.tmpdir))        

        return render_template('complete.html',battery_dest=battery_dest)

def clean_up(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    
# This is how the command line version will run
def start(port=8088):
    if port==None:
        port=8088
    print("Nobody ever comes in... nobody ever comes out...")
    webbrowser.open("http://localhost:%s" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
