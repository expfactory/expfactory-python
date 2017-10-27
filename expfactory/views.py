'''
views.py: part of expfactory package

Copyright (c) 2016-2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


'''

from expfactory.logman import bot
from expfactory.server import app
import os


# EXPERIMENT ROUTER ###########################################################
@app.route('/finish')
def router():

    #TODO: need to figure out how to serve from directory AND add static.. posts?
    # data in browser?
    #TODO: decide how we decide if it's finished. Is there a local result database?
    # Do we use an internal database? Are the views required to post OR save?
    return render_template('battery.html')


# WEB INTERFACE VIEWS ##############################################



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
        for field,value in request.form.iteritems():
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
        for field,value in request.form.iteritems():
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
