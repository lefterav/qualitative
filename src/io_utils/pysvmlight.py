'''
Created on 27 Aug 2012

@author: lefterav
'''
from xml.etree.cElementTree import iterparse

TAG_SENT = 'judgedsentence'
TAG_SRC = 'src'
TAG_TGT = 'tgt'
TAG_DOC = 'jcml'

def get_svmlight_format(dataset):
    attribute_names = set()
    
    for parallelsentence in dataset.get_parallelsentences():
        current_attribute_names = parallelsentence.get_nested_attribute_names()
        attribute_names.update(current_attribute_names)
    
    attribute_names = sorted(list(attribute_names))
    
    instances = [get_instance_from_parallelsentence(parallelsentence) for parallelsentence in dataset.get_parallelsentences()]
    return instances
        
def get_instance_from_parallelsentence(parallelsentence, attribute_names):
    current_attributes = parallelsentence.get_nested_attributes()
    label = current_attributes["rank"]
    del(current_attributes["rank"])
    new_attributes = []
    for att, value in current_attributes.iteritems():
        att_id = 1.0 * float(attribute_names.index(att))
        try:
            value = float(value)
        except:
            continue
        new_attributes.append((att_id, 1.0 * value))
    instance = (int(label), new_attributes)
    return instance


def get_attribute_names(input_filename):
    '''
    Parse once the given XML file and return a set with the attribute names
    @param input_filename: The XML file to be parsed
    '''
    source_file = open(input_filename, "r")
    # get an iterable
    context = iterparse(source_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()

    number_of_targets = 0
    attribute_names = []
    for event, elem in context:
        #new sentence: get attributes
        if event == "start" and elem.tag == TAG_SENT:
            attribute_names.extend(elem.attrib.keys())   
            target_id = 0         
        #new source sentence
        elif event == "start" and elem.tag == TAG_SRC:
            source_attributes = ["src_{}".format(key) for key in elem.attrib.keys()]
            attribute_names.extend(source_attributes)
        #new target sentence
        elif event == "start" and elem.tag == TAG_TGT:
            target_id += 1
            target_attributes = ["tgt_{}".format(key) for key in elem.attrib.keys()]
            attribute_names.extend(target_attributes)
        elif event == "end" and elem.tag == TAG_SENT:
            if target_id > number_of_targets:
                number_of_targets = target_id
        root.clear()
    source_file.close()
    return set(attribute_names)


def read_file_incremental(input_filename, meta_attributes, class_name = "tgt_rank", group_test=False, id_start = 0):

    
    attribute_names = get_attribute_names(input_filename) - set(meta_attributes)
    attribute_names = sorted(list(attribute_names))
    
    source_file = open(input_filename, "r")
    # get an iterable
    context = iterparse(source_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    
    instances = []
    instancegroups = []
    
    attributes = []
    target_id = 0
    i = id_start
    for event, elem in context:
        #new sentence: get attributes
        if event == "start" and elem.tag == TAG_SENT:
            general_attributes = elem.attrib
            i +=1 
            attribute_list = []
            target_id = 0
        #new source sentence
        elif event == "start" and elem.tag == TAG_SRC:
            source_attributes = [("src_{}".format(key), value) for key, value in elem.attrib.iteritems()]

        #new target sentence
        elif event == "start" and elem.tag == TAG_TGT:
            target_id += 1
            target_attributes = [("tgt_{}".format(key), value) for key, value in elem.attrib.iteritems()]
            attribute_list = []
            attribute_list.extend(source_attributes)
            attribute_list.extend(target_attributes)
            attributes = dict(attribute_list)
            attributes.update(general_attributes)
            label = attributes[class_name]
            del(attributes[class_name])
            
            new_attributes = []
            for att, value in attributes.iteritems():
                try:
                    att_id = int(attribute_names.index(att))
                except ValueError: #maybe it is a meta
                    continue
                try:
                    value = float(value)
                except:
                    continue
                new_attributes.append((att_id, 1.0 * value))
            instance = (int(label), new_attributes, i)
            instances.append(instance)
        
        elif event == "end" and elem.tag == TAG_SRC:
            pass
        elif event == "end" and elem.tag == TAG_TGT:
            pass
        elif event == "end" and elem.tag in TAG_SENT:
            if group_test:
                instancegroups.append(instances)
                instances = []
        
        root.clear()
    source_file.close()
    if group_test:
        return instancegroups
    return instances