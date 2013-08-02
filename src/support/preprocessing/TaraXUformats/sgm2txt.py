from xml.etree import cElementTree
import sys
import codecs

input_filename = sys.argv[1]
input_filename_fixed = input_filename.replace('.sgm', '.fixed.sgm') 

try:
    limit = int(sys.argv[2])
except:
    limit = None

try:
    lang = int(sys.argv[3])
except:
    lang = 'en'



output_filename = input_filename.replace('.sgm', '.src')
ids_filename = input_filename.replace('.sgm', '.ids')


#fix illegal chars
input_file = open(input_filename, 'r')
input_fixed_file = open(input_filename_fixed, 'w')

for line in input_file:
    line = line.replace("&", "&amp;")
    input_fixed_file.write(line)
input_fixed_file.close()
input_file.close()

    
input_file = open(input_filename_fixed, 'r')
output_file = codecs.open(output_filename, 'w', 'utf-8')
ids_file = codecs.open(ids_filename, 'w', 'utf-8')

uids = []

count = 0

context = cElementTree.iterparse(input_file, events=("start", "end"))
# turn it into an iterator
context = iter(context)
# get the root element
event, root = context.next()

setid = "{}_".format(root.attrib['setid'])

for event, elem in context:
    if event == "start" and elem.tag == "seg":
        id = elem.attrib['id']
        
        text = elem.text
        
        if not text:
            text = ""
        
        uid = "{}{}{}_{}".format(setid, docid, id, lang)
        
        uids.append(uid)
        
        output_file.write(text)
        output_file.write("\n")
        
        ids_file.write(uid)
        ids_file.write("\n")
        
        count += 1
        if limit and count>limit:
            break
        
    elif event == "start" and elem.tag == "doc":
        docid = "{}_".format(elem.attrib['docid'])
    elif event == "start" and elem.tag == "srcset":
        print "open set"
        setid = "{}_".format(elem.attrib['setid'])
        
    root.clear()

unique_ids = set(uids)
assert (len(uids)==len(unique_ids))

input_file.close()
output_file.close()
ids_file.close()
    
        
        