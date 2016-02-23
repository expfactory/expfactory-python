'''
survey.py: part of expfactory package
Functions to work with javascript surveys

'''

from glob import glob
import pandas
import json
import uuid
import re
import os

def get_question_types():
   '''get_question_types returns a list of possible question types
   '''
   return ["radio","checkbox","textfield","textarea","numeric","table","instruction"]


def create_instruction(text,id_attribute,tag="h2"):
    '''create_instruction creates a tag of type [tag] with some text inside, useful for description or instructions.
    :param text: the text to give in the instruction.
    :param id_attribute: the unique id for the question
    :param tag: the html tag for the instruction (eg, p or h2)
    '''
    return "<%s>%s</%s><br><br><br><br>" %(tag,text,tag)


def format_options_values(options,values):
    if isinstance(options,str):
        options = [options]
    if isinstance(values,str):
        values = [values]
    return options,values

def get_required_string(required_boolean):
    required = ""
    if required == 1:
        required = "required"
    return required

def create_radio(text,id_attribute,options,values,classes=None,required=0):
    '''create_radio generate a material lite radio button given a text field, and a set of options.
    :param text: The text (content) of the question to ask
    :param id_attribute: the unique id for the question
    :param options: a list of text options for the user to select from (not the value of the field)
    :param values: a list of values for corresponding options
    :param classes: the classes to apply to the label. If none, default will be used.
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    if classes == None:
        classes = "mdl-radio mdl-js-radio mdl-js-ripple-effect"

    options,values = format_options_values(options,values)
    
    required = get_required_string(required)

    if len(options) == len(values):
        radio_html = "<p>%s</p>" %(text)
        for n in range(len(options)):
            option_id = "%s_%s" %(id_attribute,n)
            radio_html = '%s\n<label class="%s" for="option-%s">\n<input type="radio" id="option-%s" class="mdl-radio__button %s" name="%s_options" value="%s">\n<span class="mdl-radio__label">%s</span>\n</label>' %(radio_html,classes,option_id,option_id,required,id_attribute,values[n],options[n])
        return "%s<br><br><br><br>" %(radio_html)
        
    print "ERROR: %s options provided, and only %s values. Must define one option per value." %(len(options),len(values))
    return ""

def create_checkbox(text,id_attribute,options,classes=None,required=0):
    '''create_checkbox generate a material lite checkbox field given a text field, and a set of options.
    :param text: The text (content) of the question to ask
    :param options: a list of text options for the user to select from
    :param id_attribute: the unique id for the question
    :param classes: the classes to apply to the label. If none, default will be used.
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    if classes == None:
        classes = "mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect"

    required = get_required_string(required)

    checkbox_html = "<p>%s</p>" %(text)
    for n in range(len(options)):
        option_id = "%s_%s" %(id_attribute,n)
        checkbox_html = '%s\n<label class="%s" for="checkbox-%s">\n<input type="checkbox" id="checkbox-%s" class="mdl-checkbox__input %s">\n<span class="mdl-checkbox__label">%s</span>\n</label>' %(checkbox_html,classes,option_id,option_id,required,options[n])
    return "%s<br><br><br>" %(checkbox_html)
    
def base_textfield(text,box_text=None,classes=None):
    '''format_textfield parses input for a general textfield, returning base html, box_text, and id.
    :param text: Any text content to precede the question field (default is None)
    :param box_text: text content to go inside the box (default is None)
    :param classes: the classes to apply to the input. If none, default will be used.
    '''        
    if box_text == None:
        box_text = ""

    textfield_html = ""
    if text != None:
        textfield_html = "<p>%s</p>" %(text)

    return textfield_html,box_text


def create_textfield(text,id_attribute,box_text=None,classes=None):
    '''create_textfield generates a material lite text field given a text prompt.
    :param text: Any text content to precede the question field (default is None)
    :param id_attribute: the unique id for the question
    :param box_text: text content to go inside the box (default is None)
    :param classes: the classes to apply to the input. If none, default will be used.
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    if classes == None:
        classes = "mdl-textfield mdl-js-textfield"

    textfield_html,box_text = base_textfield(text,box_text)
    required = get_required_string(required)

    return '%s\n<div class="%s">\n<input class="mdl-textfield__input %s" type="text" id="%s">\n<label class="mdl-textfield__label" for="%s">%s</label>\n</div><br><br><br>' %(textfield_html,classes,required,id_attribute,id_attribute,box_text)


def create_numeric_textfield(text,id_attribute,box_text=None,classes=None):
    '''create_numeric generates a material lite numeric text field given a text prompt.
    :param text: Any text content to precede the question field (default is None)
    :param id_attribute: the unique id for the question
    :param box_text: text content to go inside the box (default is None)
    :param id_attribute: an id to match to the text field
    :param classes: the classes to apply to the input. If none, default will be used.
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    if classes == None:
        classes = "mdl-textfield mdl-js-textfield"

    required = get_required_string(required)
    textfield_html,box_text = base_textfield(text,box_text)

    return '%s\n<div class="%s">\n<input class="mdl-textfield__input required" type="text" pattern="-?[0-9]*(\.[0-9]+)?" id="%s">\n<label class="mdl-textfield__label" for="%s">%s</label>\n<span class="mdl-textfield__error">Input is not a number!</span>\n</div><br><br><br>' %(textfield_html,classes,required,id_attribute,id_attribute,box_text)


def create_select_table(text,id_attribute,df,classes=None,required=0):
    '''create_select_table generates a material lite table from a pandas data frame.
    :param df: A pandas data frame, with column names corresponding to columns, and rows
    :param id_attribute: the unique id for the question
    :param text: A text prompt to put before the table
    :param classes: the classes to apply to the input. If none, default will be used.
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    if isinstance(df,pandas.DataFrame):
    
        if classes == None:
            classes = "mdl-data-table mdl-js-data-table mdl-data-table--selectable mdl-shadow--2dp %s" %(required)

        required = get_required_string(required)
        table_html = '<p>%s</p>\n<table id="%s" class="%s">\n<thead>\n<tr>' %(text,id_attribute,classes)

        # Parse column names
        column_names = df.columns.tolist()
        for column_name in columns_names:
            table_html = '%s\n<th class="mdl-data-table__cell--non-numeric">%s</th>' %(table_html,column_name)
        table_html = "%s\n</tr>\n</thead>\n<tbody>" %(table_html)

        # Parse rows
        for row in df.iterrows():
            row_id = row[0]
            table_html = "%s\n<tr>" %(table_html)
            values = row[1].tolist()
            for value in values:
                if isinstance(value,str) or isinstance(value,unicode):
                    table_html = '%s\n<td class="mdl-data-table__cell--non-numeric">%s</td>' %(table_html,str(value))
                else:
                    table_html = '%s\n<td>%s</td>' %(table_html,value)
            table_html = "%s\n</tr>" %(table_html)
        return "%s\n</tbody>\n</table><br><br><br>" %(table_html)
 
    print "ERROR: DataFrame (df) must be a pandas.DataFrame"


def create_textarea(text,id_attribute,classes=None,rows=3,required=0):
    '''create_textarea generates a material lite multi line text field with a text prompt.
    :param text: A text prompt to put before the text field
    :param id_attribute: the unique id for the question
    :param classes: the classes to apply to the textfield div. If none, default will be used.
    :param rows: number of rows to include in text field (default 3)
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    textfield_html,box_text = base_textfield(text,box_text)

    if classes == None:
        classes = "mdl-textfield mdl-js-textfield"
    return '%s\n<div class="%s"><textarea class="mdl-textfield__input %s" type="text" rows= "%s" id="%s" ></textarea>\n<label class="mdl-textfield__label" for="%s">%s</label></div><br><br><br>' %(textfield_html,classes,required,rows,id_attribute,id_attribute)


def parse_questions(question_file,exp_id,delim="\t"):
    '''parse_questions reads in a text file, separated by delim, into a pandas data frame, checking that all column names are provided.
    :param question_file: a TAB separated file to be read with experiment questions. Will also be validated for columns names.
    :param exp_id: the experiment unique id, to be used to generate question ids
    '''
    df = pandas.read_csv(question_file,sep=delim)
    required_columns = ["question_type","question_text","page_number","option_text","option_values","required"]
    optional_columns = ["variables"]
    acceptable_types = get_question_types()

    # Parse column names, ensure lower case, check that are valid
    column_names = [x.lower() for x in df.columns.tolist()]
    acceptable_columns = []
    for column_name in column_names:
        if column_name in required_columns + optional_columns:
            acceptable_columns.append(column_name)

    # Make sure all required columns are included
    if len([x for x in required_columns if x in acceptable_columns]) == len(required_columns):
 
        # Each question will have id [exp_id][question_count] with appended _[count] for options
        question_count = 0
        df.columns = acceptable_columns
        questions = []
        current_page_number = 1
        current_page = '<div class="step">'
        for question in df.iterrows():

            question_type = question[1].question_type
            question_text = question[1].question_text
            page_number = question[1].page_number
            options = question[1].option_text
            values = question[1].option_values
            required = question[1].required
            unique_id = "%s_%s" %(exp_id,question_count)
            new_question = None

            if question_type in acceptable_types:

                # Instruction block / text
                if question_type == "instruction":
                    new_question = create_instruction(question_text,tag="h3",id_attribute=unique_id)
                
                # Radio button
                elif question_type == "radio":
                    if not str(options) == "nan" and not str(values) == "nan":
                        new_question = create_radio(text=question_text,
                                                      options=options.split(","),
                                                      values = values.split(","),
                                                      required=required,
                                                      id_attribute=unique_id)
                    else:
                        print "Radio question %s found null for options or values, skipping." %(question_text)
 
                # Checkbox
                elif question_type == "checkbox":
                    if not str(options) == "nan":
                        new_question = create_checkbox(text=question_text,
                                                       options=options,
                                                       required=required,
                                                       id_attribute=unique_id)
                    else:
                        print "Checkbox question %s found null for options, skipping." %(question_text)

                # Textareas and Textfields, regular and numeric
                elif question_type == "textarea":
                    new_question = create_textarea(question_text,
                                                   required=required,
                                                   id_attribute=unique_id)

                elif question_type == "textfield":
                    new_question = create_textfield(question_text,
                                                    required=required,
                                                    id_attribute=unique_id)

                elif question_type == "numeric":
                    new_question = create_numeric_textfield(question_text,
                                                            required=required,
                                                            id_attribute=unique_id)


                # Table
                elif question_type == "table":
                    print "Table option not yet supported! Coming soon."
 
                question_count+=1
            
            if new_question != None:
                # Add the new question to the current page
                if page_number == current_page_number:                 
                    current_page = "%s\n%s" %(current_page,new_question)
                # Save the current page, add the current question to the next page
                else:
                    questions.append("%s</div>" %current_page)
                    current_page = '<div class="step">\n%s' %new_question
                    current_page_number = page_number

        # Add the last page
        questions.append("%s</div>" %current_page)
        return questions
    else:
        return None



def generate_survey(experiment,experiment_folder,form_action="#",classes=None,survey_file="survey.tsv"):
    '''generate_survey takes a list of questions and outputs html for an expfactory survey
    :param experiment: The experiment loaded config.json
    :param experiment_folder: should contain survey.tsv, a TAB separated file with question data. Will be read into a pandas data frame, and columns must follow expfactory standard. Data within columns is separated by commas.
    :param form_action: the form action to take at the bottom of the page
    :param classes: the classes to apply to the outer content div. If none, default will be used
    :param survey_file: the survey file, should be survey.tsv for a valid survey experiment
    '''       
    if classes == None:
        classes = "experiment-layout mdl-layout mdl-layout--fixed-header mdl-js-layout mdl-color--grey-100"

    # We will generate unique ids for questions based on the exp_id
    exp_id = experiment[0]["exp_id"]
    question_file = "%s/%s" %(experiment_folder,survey_file)

    questions = parse_questions(question_file,exp_id=exp_id)

    if questions != None:
        survey = '<div class="%s">\n<div class="experiment-ribbon"></div>\n<main class="experiment-main mdl-layout__content">\n<div class="experiment-container mdl-grid">\n<div class="mdl-cell mdl-cell--2-col mdl-cell--hide-tablet mdl-cell--hide-phone">\n</div>\n<div class="experiment-content mdl-color--white mdl-shadow--4dp content mdl-color-text--grey-800 mdl-cell mdl-cell--8-col">\n\n<div id="questions">\n\n<form name="questions" action="%s">' %(classes,form_action)

        for question in questions:
            survey = "%s\n%s" %(survey,question)       
        return survey
    else:
        print "ERROR: parsing input text file survey.tsv. Will not generate survey HTML"
