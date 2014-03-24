import sys

def dedupe(source_filename, target_filename):

    source_file = open(source_filename)
    target_file = open(target_filename)
    output_source_file = open(source_filename+".dedup", 'w')
    output_target_file = open(target_filename+".dedup", 'w')
    
    seen = {}
    output = []
    total = 0
    kept = 0
    keyerror = 0
    
    #iterate over source and target sentences
    for source_line in source_file:

        source_line = source_line
        target_line = target_file.readline()
        total+=1
         
        try:
            #map possible translations to EACH source sentence via a set
            l = len(seen)
            seen[source_line].add(target_line)
            
            #if translation for this source sentence exists but
            # incoming translation hasn't seen before for this source
            # add it and count it
            if len(seen) > l:
                output_source_file.write(source_line)
                output_target_file.write(target_line)
                kept+=1
            
            #else sentence is ignored

        #if source sentence hasn't seen before add it to the dict now    
        except KeyError:
            keyerror+=1
            kept+=1
            seen[source_line] = set([target_line])
            output_source_file.write(source_line)
            output_target_file.write(target_line)
            
    #print stats
    print "Kept {} of {} ({} %)".format(kept, total, (100.00*kept/total))
    print "{} source sentences had more than one translation each".format(kept-keyerror)
    source_file.close()
    target_file.close()
    output_source_file.close()
    output_target_file.close()

if __name__ == '__main__':
    dedupe(sys.argv[1], sys.argv[2])
