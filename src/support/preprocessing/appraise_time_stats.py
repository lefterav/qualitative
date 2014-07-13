'''
Created on 1 Aug 2012

@author: Eleftherios Avramidis
'''

from xml.etree.cElementTree import iterparse
from datetime import datetime
import sys

class Item:
    def __init__(self):
        self.duration = None
        self.id = None
        self.tokens = None


def miniparse(filename):
    """
    Read taraXU post-editing from filename and return a shallow list of 
    tree items with specific variables set 
    
    """
    timeformat_long = '%H:%M:%S.%f'
    timeformat_short = '%H:%M:%S'
    s0 = '00:00:00.000000'
    nulltime = datetime.strptime(s0, timeformat_long)
    
    file = open(filename, "r")
    context = iterparse(file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    
    items = {}
    
    item = None
    for event, elem in context:
        
        if event == "start" and elem.tag == "post-editing-item":
            try:
                item = Item()
                item.fromscratch = elem.attrib["from-scratch"]
                item.fromscratch = True
            except:
                item.fromscratch = False
            item.id = elem.attrib["id"]
            duration_string = elem.attrib["duration"]
            try:
                duration_delta = datetime.strptime(duration_string, timeformat_long) - nulltime
            except ValueError:
                try:
                    duration_delta = datetime.strptime(duration_string, timeformat_short) - nulltime
                except:
                    root.clear()
                    continue
            
            item.duration = duration_delta.seconds # + 0.000001 * duration_delta.microseconds
            
        if event == "end" and elem.tag == "post-editing-item":
            try:
                text = list(elem)[0].text
                item.length = len(text)
                item.tokens = len(text.split(' ')) 
                
            except:
#                print "-",
                continue 
        
#        if item.id:
#            print "+",
            if item.duration > 300:
                continue
            items.setdefault(item.id, []).append(item)
#        print
        root.clear()
    file.close()
    return items


filename = sys.argv[1]

items_all = miniparse(filename)


durations_1 = []
durations_2 = []

durations_clustered_1 = {}
durations_clustered_2 = {}

cluster_interval = 20

#now count all items with the same id 
for id, id_items in items_all.iteritems():
    for item_1 in id_items:
        #print item_1.id, item_1.duration
        if item_1.fromscratch:
            #print
            try:
                similar_items = items_all[id]
            except KeyError:
                continue
            durations = []
            for similar_item in similar_items:
                if not similar_item.fromscratch:
                    durations.append(similar_item.duration)
            if durations:
                avg_duration = float(sum(durations)) / len(durations)
                durations_1.append(item_1.duration)    
                durations_2.append(avg_duration)
                
                token_class = item_1.tokens / cluster_interval * cluster_interval #this is integer division
                durations_clustered_1.setdefault(token_class, []).append(item_1.duration)
                durations_clustered_2.setdefault(token_class, []).append(avg_duration)
                
for duration_cluster, durations in durations_clustered_1.iteritems():
    print "[{},{}]".format(duration_cluster,duration_cluster+cluster_interval-1),
    print float(sum(durations)) / len(durations)

for duration_cluster, durations in durations_clustered_2.iteritems():
    print "[{},{}]".format(duration_cluster,duration_cluster+cluster_interval-1),
    print float(sum(durations)) / len(durations)
        
    

print "Found {} aligned post-editings from scratch".format(len(durations_1))
print float(sum(durations_1)) / len(durations_1) , float(sum(durations_2)) / len(durations_2) 




        
        
        
         
        
