'''
analysis.py: part of efactory package
Functions for analyses with psiturk results

'''

# Code below is from ieisenberg, not yet modified (turned into functions) for package, just storage only!

# -*- coding: utf-8 -*-

import yaml
import json
import pandas as pd

file_path = '/Users/Ian/Downloads/Cognitive_Control_Ontology (1).yml'
f = open(file_path, 'r')

'''
Data comes off the MySQL server in whatever form you download it. Here we have downloaded
it as a YAML file. So the first thing is to parse the yaml file. This will return a list,
where each entry is an individual document (an individual subject completing one HIT)
'''
yaml_data = yaml.load(open('/Users/Ian/Downloads/Cognitive_Control_Ontology (1).yml', 'r'))

'''
Once we have the yaml file parsed, we can select a particular subject. Each subject's information
is stored in a dictionary. The element of interest is a 'datastring' which is stored in 
JSON format.

For reference, the keys of each yaml file document are below:
['datastring', 'uniqueid', 'platform', 'browser', 'counterbalance', 'beginhit', 'assignmentid', 
'cond', 'codeversion', 'language', 'ipaddress', 'workerid', 'bonus', 'status', 'endhit', 'hitid']

'''

subj = 0 #index of document in yaml file
#Have to check if this is identifiable
subj_ID = yaml_data[subj]['workerid']
subj_data = json.loads(yaml_data[subj]['datastring'])

'''
The JSON file is itself a dictionary with the following keys:
['bonus', 'useragent', 'assignmentId', 'counterbalance', 'condition', 'hitId', 
'data', 'eventdata', 'currenttrial', 'workerId', 'questiondata']

'Eventdata' and 'questiondata' are psiturk terms which record data that you have
specifically directed to them. In general, we want 'data'
'''
subj_data = subj_data['data']

'''
The data file is a list of dictionaries with some superfluous information. The keys are below:
dict_keys(['uniqueid', 'current_trial', 'dateTime', 'trialdata'])

After you remove this, subj_data is now a list of dictionaries with only the data we care about
'''
subj_data = [trial['trialdata'] for trial in subj_data]
#convert to pandas df
df = pd.DataFrame(subj_data)
#append id
df['id']=subj_ID
'''
SPECIFIC TO COGNITIVE ONTOLOGY
There are many 'trials' that don't include any relevant data. Trials with relevant data
will at least have a non-null exp_id
'''
df = df[pd.notnull(df.exp_id)]

#resets the trial index from the arbitrary coding to 0->n
df.reset_index(inplace = True)
df['trial_index'] = df.index

#drop unnecessary columns
df.drop(['internal_chunk_id', 'trial_index_global', 'index'],axis = 1, inplace = True)

