#!/usr/bin/env python

'''
graph.py: part of pybraincompare package
Functions to work with ontology graphs

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
from expfactory.utils import get_installdir, get_template, sub_template
import re
import sys
import json
import numpy
import pandas
from logman import bot
import UserDict

class Node(object):
    def __init__(self, nid, parent, name, meta=None):
        self.nid = nid
        self.parent = parent
        self.children = []
        self.name = name
        self.meta = [meta] # should be dictionary!

def get_json(nodes):
    '''get_json
    return a json graph structure for a set of nodes

    :param nodes: list of pybraincompare.ontology.graph.Node
        a list of nodes. The root node should have node.nid == 1
    '''
    tree = dict()
    # Make an empty node object for each node
    for node in nodes:
        tree[node.nid] = {"nid":node.nid, "name":node.name, "meta":node.meta,"children":[]}
    # Add base nodes to the queue
    expression = re.compile("node_*")
    queue = [child for child in nodes if expression.search(child.nid)]
    remainder = [child for child in nodes if child not in queue]

    # We will keep a list of nodes with no parents
    missing_parents = []

    while queue:
        current = queue.pop()
        # Get json of node
        node = tree[current.nid]
        # Remove child from the tree
        new_tree = dict() # This has to be done for python 2.6 support
        for k,v in tree.iteritems():
           if k != current.nid:
               new_tree[k] = v
        tree = new_tree
        # Append as child to all parent json
        parents = current.parent
        for parent in parents:
            if parent != "None" and parent in tree:
                tree[parent]["children"].append(node)
            else:
                missing_parents.append(node)

    # Only keep nodes (experiments) missing parents
    missing_parents = [x for x in missing_parents if re.search("node_",x["nid"])]

    while remainder:
        current = remainder.pop()        
        # Get json of node
        node = tree[current.nid]
        # Append as child to all parent json
        parents = current.parent
        for parent in parents:
            if parent != "None":
                tree[parent]["children"].append(node)

    # For now, just remove first level of children that don't have children
    root = tree["1"]
    new_children = []
    for child in root["children"]:
        if child["children"]: # remove empty concepts
            new_children.append(child)

    # Add experiments on that don't have concept parents
    new_children = new_children + missing_parents

    root["children"] = new_children

    return root


# Utils
def check_pandas_columns(df,column_names):
    '''check_pandas_columns
    will check that a list of columns is in a data frame
    '''
    for column_name in column_names:
        if column_name not in df.columns:
            raise ValueError('column %s is missing from relationship table.' %(column_name))
            

def find_circular_reference(relationship_table):
    '''find_circular_reference
    checks to see that there are no circular references between nodes
    '''
    unique_nodes = relationship_table.id.unique().tolist()
    for node in unique_nodes:
        parents = relationship_table.parent[relationship_table.id==node].tolist()
        # Check to see that parent is not also a child of current node
        for parent in parents:
            parent_parents = relationship_table.parent[relationship_table.id==parent].tolist()
            if node in parent_parents:
                raise ValueError("ERROR: circular reference between %s and %s" %(node,parent))
    
def walk(node,parent=None,func=None):
    for child in list(node.get('children',[])):
        walk(child,parent=node,func=func)
    if func is not None:
        func(node,parent=parent)

def do_pruning(node,parent):
    if not re.search("node_",node.get("nid")) and len(node.get('children',[])) == 0:
        parent['children'].remove(node)


def get_node_by_name(myjson,name):
    '''get_node_by_name
    
    This function will "grab" a node by the name ( a subset of the tree )
    '''
    if myjson.get('name',None) == name:
        return myjson
    for child in myjson.get('children',[]):
        result = get_node_by_name(child,name)
        if result is not None:
            return result
    return None

def get_node_fields(myjson,field="name",nodes=[]):
    '''get_node_fields
    
    This function will get all the names of the nodes
    '''
    if myjson.get(field,None) == None:
        return nodes
    else: 
        nodes.append(myjson.get(field))
        for child in myjson.get('children',[]):
            nodes = get_node_fields(myjson=child,field=field,nodes=nodes)
    if not nodes: 
          return None
    return nodes


def make_tree_from_triples(triples,output_html=False,meta_data=None,delim="\t",prune_tree=True):
    '''make_tree_from_triples
    generate a tree from a data structure with the following format
    :param triples: csv or pandas data frame 
        either a file or pandas data frame with this format

    ..note::
 
                             id             parent                          name
        0                     1               None                          BASE
        1     trm_4a3fd79d096be  trm_4a3fd79d0aec1           abductive reasoning
        2     trm_4a3fd79d096e3  trm_4a3fd79d09827              abstract analogy
        3     trm_4a3fd79d096f0  trm_4a3fd79d0a746            abstract knowledge
        4     trm_4a3fd79d096fc                  1               acoustic coding
    
        The index (0-4) is not used. The head/base node should have id 1, and no parent.
        All other nodes can be unique ids that you specify, with a name.

    :param delim: the delimiter use to separate values
    :param output_html: return html page instead of json data structure
    :param prune_tree: boolean do not include nodes that don't have task children default [True]
    :param meta_data [OPTIONAL]: dict 
          if defined, should be a dictionary of dictionaries, with

    ..note::

          key = the node id
          value = a dictionary of meta data. For example:

          {
            "trm_12345":{"defined_by":"squidward","score":1.2},
            "node_54321":{"date":"12/15/15"},
          }
    
    '''
    nodes = []

    if not isinstance(triples,pandas.DataFrame):
        triples = pandas.read_csv(relationship_table,sep="\t")

    # check for correct columns and circular references
    check_pandas_columns(df=triples,column_names=["id","name","parent"])
    find_circular_reference(triples)

    # Generate nodes
    unique_nodes = triples.id.unique().tolist()
    bot.debug("%s unique nodes found." %len(unique_nodes))
    for node in unique_nodes:
        parents = triples.parent[triples.id==node].tolist()
        name = triples.name[triples.id==node].unique().tolist()
        if len(name) > 1:
            raise ValueError("Error, node %s is defined with multiple names." %node)
        meta = {}
        if meta_data:
           if node in meta_data:
               meta = meta_data[node]
        nodes.append(Node(node, parents, name[0], meta))

    # Generate json
    graph = get_json(nodes)

    if prune_tree == True:
        walk(graph,func=do_pruning)

    if output_html == True:
        # Generate the dynamic list - we will limit to three levels into the ontology
        html_snippet = ''
        # We will save a dictionary of base (experiment) nodes
        experiment_nodes = dict()
        # Save a list of nodes without concept_parents
        orphan_experiment_nodes = dict()
        for child in graph["children"]:
            # For each child, we will tag base nodes with parent ids
            parent_ids = [child["nid"]]
            # This first level cannot be a base node, so we don't check.
            # Update the experiment_nodes lookup with experiment nodes at this level
            exp_nodes = [x for x in child["children"] if re.search("node_",x["nid"])]
            if len(exp_nodes) == 0:
                orphan_experiment_nodes = add_orphan_experiment_nodes(orphan_experiment_nodes,child)
            experiment_nodes = add_experiment_nodes(experiment_nodes,exp_nodes,parent_ids)
            # Do we have all base (experiment) nodes?
            if len(exp_nodes)==len(child["children"]):
                # Children do not get added to list
                html_snippet = '%s<a><li class="accord" id="accord_%s">%s</li></a>' %(html_snippet,str(child["nid"]),str(child["name"]))                
            else:
                html_snippet = '%s<li><a id="accord_%s" class="toggle accord">%s</a>' %(html_snippet,str(child["nid"]),str(child["name"]))
                # Add non-children 
                html_snippet = html_snippet + '<ul class="inner">' 
                other_nodes = [x for x in child["children"] if not re.search("node_",x["nid"])]
                for other_node in other_nodes:
                    sub_parent_ids = parent_ids[:]
                    sub_parent_ids.append(other_node["nid"])
                    # Update the experiment_nodes lookup with experiment nodes at this level
                    exp_nodes = [x for x in other_node["children"] if re.search("node_",x["nid"])]
                    if len(exp_nodes) == 0:
                        orphan_experiment_nodes = add_orphan_experiment_nodes(orphan_experiment_nodes,other_node)
                    experiment_nodes = add_experiment_nodes(experiment_nodes,exp_nodes,sub_parent_ids)
                    # Do we have all base (experiment) nodes?
                    if len(exp_nodes)==len(other_node["children"]):
                        html_snippet = '%s<a><li id="accord_%s" class="accord">%s</li></a>' %(html_snippet,str(other_node["nid"]),str(other_node["name"]))
                    else:
                        html_snippet = '%s<li><a id="accord_%s" class="toggle accord">%s</a>' %(html_snippet,str(other_node["nid"]),str(other_node["name"]))
                        html_snippet = html_snippet + '<ul class="inner">' 
                        # Add non children
                        last_nodes = [x for x in other_node["children"] if not re.search("node_",x["nid"])]     
                        for last_node in last_nodes:
                            last_parent_ids = sub_parent_ids[:]
                            last_parent_ids.append(last_node["nid"])
                            # One last final go to update experiment nodes
                            exp_nodes = [x for x in last_node["children"] if re.search("node_",x["nid"])]
                            if len(exp_nodes) == 0:
                                orphan_experiment_nodes = add_orphan_experiment_nodes(orphan_experiment_nodes,last_node)
                            experiment_nodes = add_experiment_nodes(experiment_nodes,exp_nodes,last_parent_ids)
                            if len(exp_nodes)==len(last_node["children"]):
                                html_snippet = '%s<a><li id="accord_%s" class="accord">%s</li></a>' %(html_snippet,str(last_node["nid"]),str(last_node["name"]))
                            else:
                                html_snippet = '%s<li><a href="#" id="accord_%s" class="toggle accord">%s</a>' %(html_snippet,str(last_node["nid"]),str(last_node["name"]))
                                html_snippet = html_snippet + '<ul class="inner">' 
                                base_nodes = [x for x in last_node["children"] if not re.search("node_",x["nid"])]             # Regardless of more layers, we generate links here for all remaining base_node links.
                                for base_node in base_nodes:
                                    html_snippet = '%s<a><li class="accord" id="accord_%s">%s</li></a>' %(html_snippet,str(base_node["nid"]),str(base_node["name"]))
                                    base_parent_ids = last_parent_ids[:]
                                    base_parent_ids.append(base_node["nid"])
                                    remaining_children = []
                                    remaining_parents = [base_node]
                                    while len(remaining_parents) > 0:
                                        current_node = remaining_parents.pop(0)
                                        remaining_children = remaining_children + [x for x in current_node["children"] if re.search("node_",x["nid"])]
                                        remaining_parents = remaining_parents + [x for x in current_node["children"] if not re.search("node_",x["nid"])]
                                    experiment_nodes = add_experiment_nodes(experiment_nodes,remaining_children,base_parent_ids)
                                html_snippet = "%s</ul></li>" %(html_snippet)
                        html_snippet = "%s</ul></li>" %(html_snippet)
                html_snippet = html_snippet + "</ul></li>"     
           
        # Now we will generate html for each of the experiments, and save a lookup by concept id as we go
        concept_lookup = dict()
        html_experiments = ''
        orphan_experiment_nodes.update(experiment_nodes)
        for experiment_node,node in orphan_experiment_nodes.iteritems():
            # If we have meta data, present each as a little paragraph.
            meta_snippet=''
            if meta_data != None:
                if node["nid"] in meta_data:
                    meta_single = meta_data[node["nid"]]
                    for meta_tag,meta_value in meta_single.iteritems():
                        if meta_tag != "experiment_variables":
                            if isinstance(meta_value,list):
                                meta_value = ",".join(meta_value)
                            meta_snippet = "%s<p><strong>%s</strong>: %s</p>" %(meta_snippet,meta_tag,meta_value)
            html_experiments = '%s<div id="exp_%s" class="panel panel-default"><div class="alert-info" style="padding-left:10px;background-color:#F2DF49">%s</div><div class="panel-body"><p>%s</p><a href="https://expfactory.github.io/%s.html" target="_blank" class="btn btn-default">Preview Experiment</a></div></div>\n' %(html_experiments,node["name"],node["name"],meta_snippet,node["name"])    
            for parent in node["parents"]:
                if str(parent) in concept_lookup:
                    holder = concept_lookup[str(parent)]
                    holder.append(experiment_node)
                    concept_lookup[str(parent)] = holder
                else:
                    concept_lookup[str(parent)] = [experiment_node]
            # If the node is an experiment and has only root parent, add to lookup
            if len(node["parents"])==1:
                if node["parents"][0]=="1":
                    concept_lookup[node["nid"]] = [experiment_node]
        # All experiments
        concept_lookup["all_experiments"] = orphan_experiment_nodes.keys()

        # Plug everything into the template
        template = get_template("%s/templates/experiments_categories.html" %get_installdir())
        template = sub_template(template,"[[SUB_LOOKUP_SUB]]",str(concept_lookup))
        template = sub_template(template,"[[SUB_EXPERIMENTS_SUB]]",html_experiments)
        template = sub_template(template,"[[SUB_NAVIGATION_SUB]]",html_snippet)           
        graph = template        
    return graph


def add_experiment_nodes(experiment_node_dict,new_nodes,parent_ids):
    '''add_experiment_nodes updates an experiment_nodes dictionary with new nodes
    :param experiment_node_dict: dictionary to be updated, nid is key, node dictionary is value
    :param new_nodes: nodes to update dictionary
    :param parent_ids: updated parent ids for nodes
    '''
    if not isinstance(parent_ids,list):
        parent_ids = [parent_ids]
    for new_node in new_nodes:
        if new_node["name"] in experiment_node_dict:
            holder = experiment_node_dict[new_node["name"]]
            holder["parents"] = numpy.unique(holder["parents"] + parent_ids).tolist()
            experiment_node_dict[new_node["name"]] = holder
        else:
            experiment_node_dict[new_node["name"]] = new_node
            experiment_node_dict[new_node["name"]]["parents"] = parent_ids  
    return experiment_node_dict


def add_orphan_experiment_nodes(experiment_node_dict,new_node):
    '''add_experiment_nodes updates an experiment_nodes dictionary with new nodes
    :param experiment_node_dict: dictionary to be updated, nid is key, node dictionary is value
    :param new_node: orphan node to update dictionary
    '''
    if new_node["name"] not in experiment_node_dict and re.search("node_",new_node["nid"]):
        experiment_node_dict[new_node["name"]] = new_node
        experiment_node_dict[new_node["name"]]["parents"] = ["1"]  
    return experiment_node_dict
