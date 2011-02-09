import re, time, random, sys, gzip


def getHTMLaddr(xml_code, split_tag):
    return xml_code.split(split_tag)[1].split('"')[0]

# TO FINISH!!!
# change (replace) particular tags to an easier form {only for lang = 1!}
# e.g. '...<span class="acronym">DSSSL</span>...' --> '...<acronym>DSSSL</acronym>...'
def shiftTagsLang1(TAGS_2_SHIFT, html):
    for tag_name in TAGS_2_SHIFT:
        tags = re.split('<'+tag_name+'\s[^>]*class=\s*"',html)[1:]
        for tag in tags:
            core = tag.split('</'+tag_name+'>')[0]
            tag_class = core.split('"')[0]
            body = core.partition('">')[2].strip()
            html = html.replace(core, '#{#'+tag_class+'#}#'+body+'#{#/'+tag_class+'#}#') # '#{#' instead of '<'
            html = re.sub('<'+tag_name+'\s[^>]*class=\s*"','',html)
            html = re.sub('</'+tag_name+'>','',html)
    return html

# shift particular tags from outside into the <w>...</w> {only for lang = 0!}
def shiftTagsLang0(TAGS_2_SHIFT, html):
    for tag_name in TAGS_2_SHIFT:
        tags = re.split('<'+tag_name+'\s[^>]*class=\s*"',html)[1:]
        #print len(tags), time.time()
        for tag in tags:
            #print time.time()
            core = tag.split('</'+tag_name+'>')[0]
            inFront = core.partition('<w>')[0]
            tag_class = core.split('"')[0]
            body = core.partition('<w>')[2].rpartition('</w>')[0].strip()
            behind = core.rpartition('</w>')[2]
            try:
                html = html.replace(core, inFront+'<w><'+tag_class+'>'+body+'</'+tag_class+'></w>'+behind)
            except:
                print tag_name, tag, core, inFront, tag_class, body, behind
    return html

def getXTargets(xml_code, id_st):
    xtargets = []
    for piece1 in xml_code.split('xtargets="')[1:]:
        piece2 = ''
        # xtargets src
        if id_st == 0: piece2 = piece1.split('"')[0].split(';')[0].strip()
        # xtargets tgt
        if  id_st == 1: piece2 = piece1.split('"')[0].split(';')[1].strip()
        xtargets.append(piece2)
    return xtargets

# connect all words in <w>...</w> into 1 fragment
def getFragment(wTagStr):
    fragment = ''
    for wTag in re.findall('<w>.*?</w>', wTagStr, re.DOTALL):
        fragment = fragment + wTag.split('<w>')[1].split('</w>')[0].strip() + ' '
    return fragment

# remove tags from sentence and replace '#{#' with '<' (used in shiftTagsLang1() to newly preserve created tags)
def getSentence(wTagStr):
    fragment = re.sub('<.*?>','',wTagStr)
    fragment = fragment.replace('#{#','<').replace('#}#','>')
    return fragment

def getFragments(sen, html, lang):
    wTagStr = ''
    fragment = ''
    if sen.count(' ') > 0:
        for multiSen in sen.split(' '):
            try:
                    wTagStr = wTagStr + re.split('<s\s[^>]*"'+multiSen+'">', html, re.DOTALL)[1].split('</s>')[0]
            except IndexError:
                    pass
    else:
        wTagStr = re.split('<s\s[^>]*"'+sen+'">', html, re.DOTALL)[1].split('</s>')[0]
    if lang == 0: # common languages (English, German...)
        fragment = getFragment(wTagStr)

    elif lang == 1: # Asia languages (Chinese, Japanese...)
        fragment = getSentence(wTagStr)
    return fragment.strip()


def getFragmentList(xtargets, html, lang):
    #print html
    fragmentList = []
    for sen in xtargets:
        wTagStr = ''
        fragment = ''
        if sen.count(' ') > 0:
            for multiSen in sen.split(' '):
                try:
                        wTagStr = wTagStr + re.split('<s\s[^>]*"'+multiSen+'">', html, re.DOTALL)[1].split('</s>')[0]
                except IndexError:
                        pass
        else:
            wTagStr = re.split('<s\s[^>]*"'+sen+'">', html, re.DOTALL)[1].split('</s>')[0]
        if lang == 0: # common languages (English, German...)
            fragment = getFragment(wTagStr)
        elif lang == 1: # Asia languages (Chinese, Japanese...)
            fragment = getSentence(wTagStr)
        fragmentList.append(fragment.strip())
    return fragmentList

def getFrags2Remove(html, xtargets, addr, lang):
    removeSet = set()
    for frag in xtargets:
        if frag == '': # if frag is ''
            removeSet.add(frag)
            #print 'Sentence is empty!', frag, '! file:', addr
            #h.write('Sentence is empty! '+frag+'! file: '+addr)
        
        elif frag.count(' ') > 0:
            for frag_x in frag.split(' '):
                if html.count(frag_x) == 0: # if frag doesn't exist in html
                    removeSet.add(frag)
                    #print "Sentence(s) doesn't exist or was removed as a source code!", frag, '! file:', addr
                    #h.write("Sentence(s) doesn't exist or was removed as a source code! "+frag+'! file: '+addr)

        elif html.count(frag) == 0: # if frag doesn't exist in html
            removeSet.add(frag)
            #print "Sentence doesn't exist or was removed as a source code!!", frag, '! file:', addr
            #h.write("Sentence doesn't exist or was removed as a source code!! "+frag+'! file: '+addr)

        else:
            wTagStr = ''
            fragment = ''
            if frag.count(' ') > 0:
                for fragg in frag.split(' '):
                    wTagStr = wTagStr + re.split('<s\s[^>]*"'+fragg+'">', html, re.DOTALL)[1].split('</s>')[0]
            else:
                try:
                        wTagStr = re.split('<s\s[^>]*"'+frag+'">', html, re.DOTALL)[1].split('</s>')[0]
                except IndexError:
                        pass
            if len(re.findall('<w>.*?</w>', wTagStr, re.DOTALL)) == 0 and lang != 1:
                #print 'No fragments (<w>...<\w>) in sentence:', frag, '! file:', addr
                #h.write('No fragments (<w>...<\w>) in sentence: '+frag+'! file: '+addr)
                removeSet.add(frag)
        
    return removeSet

def removeFragments(src_addr, tgt_addr, html_src, html_tgt, xtargets_src, xtargets_tgt, items2remove_src, items2remove_tgt):
    #print 'ERROR ITEM:'
    #print 'src item2remove:', items2remove_src, 'tgt item2remove:', items2remove_tgt
    #h.write('ERROR ITEM:')
    #h.write('src item2remove: '+str(items2remove_src)+' tgt item2remove: '+str(items2remove_tgt))

    indexes = [] # a list of item indexes, which should be removed from xtargets_src and xtargets_tgt
    for item in items2remove_src:
        for i in range(len(xtargets_src)):
            # if item (e.g. 's12.1' or '') == xtargets_src[i] AND index is not yet in indexes
            if item == xtargets_src[i] and indexes.count(i) == 0: indexes.append(i)
    for item in items2remove_tgt:
        for i in range(len(xtargets_tgt)):
            # if item (e.g. 's12.1' or '') == xtargets_src[i] AND index is not yet in indexes
            if item == xtargets_tgt[i] and indexes.count(i) == 0: indexes.append(i)
    indexes.sort() # ascending sorting of indexes
    indexes.reverse() # reverse indexes (descending sorting of indexes)
    for index in indexes: # remove item from xtargets (highest item index first)
        xtargets_src.pop(index)
        xtargets_tgt.pop(index)

            

#---------------------MAIN---------------------
# ENTER A FILENAME:
inputFile = sys.argv[1]
# ENTER A LANGUAGE GROUP: 0==Europian (en, de, cs, pl...), 1==Asia (zh, ja...)
lang_src = 0
lang_tgt = 0
# TAG TO REMOVE:
PRE = '<pre\s[^>]*class=[^>]*"php">.*?</pre>'
# TAGS TO MOVE INSIDE <w>...</w>
TAGS_2_SHIFT = ['span','tt','b']

src_file = open(inputFile.split('.')[0]+'_src.txt', 'w')
print "Creating source file: %s" % src_file
tgt_file = open(inputFile.split('.')[0]+'_tgt.txt', 'w')

#h = open(inputFile.split('.')[0]+'_log.txt','w')

f = open(inputFile)
cesfile = f.read()
f.close()

i=0

for linkGrp in cesfile.split('<linkGrp')[1:]:

    linkGrp = linkGrp.split('<\linkGrp>')[0]

    # gets an address of source and target html file in a linkGrp from .ces file (example: 'PHP/php_en/html/about.howtohelp.html')
    src_addr = getHTMLaddr(linkGrp, 'fromDoc="') # OK
    tgt_addr = getHTMLaddr(linkGrp, 'toDoc="') # OK
    print '----src_file:',src_addr,'tgt_file:',tgt_addr,'----'
    #h.write('----src_file: '+src_addr+' tgt_file: '+tgt_addr+' ----')

    # gets a list of fragment numbers located in html file (example: '['s1.1', ..., 's6.3 s7.1', 's7.2', ..., 's15.1']')
    xtargets_src = getXTargets(linkGrp, 0)
    xtargets_tgt = getXTargets(linkGrp, 1)
    # open source and target html file with text fragments
    a = gzip.open("%s.gz" % src_addr)
    html_src = a.read().replace('\n',' ')
    a.close()
    b = gzip.open("%s.gz" % tgt_addr)
    html_tgt = b.read().replace('\n',' ')
    b.close()

    # remove tags that are undesired - <pre class="php">...</pre>
    html_src = re.sub(PRE,'',html_src,re.DOTALL)
    html_tgt = re.sub(PRE,'',html_tgt,re.DOTALL)

    # shift particular tags from outside into the <w>...</w> {only for lang = 0!}
    if lang_src == 0:
        html_src = re.sub('<w\s[^>]*>','<w>',html_src) # replace e.g. <w id="w5.1.1"> for <w>
        html_src = shiftTagsLang0(TAGS_2_SHIFT, html_src) # example: <b class="function"><w>XML</w></b> --> <b class="function"><w><function>XML<function></w></b>
    if lang_tgt == 0:
        html_tgt = re.sub('<w\s[^>]*>','<w>',html_tgt) # ---||---
        html_tgt = shiftTagsLang0(TAGS_2_SHIFT, html_tgt) # ---||---
        
    # change (replace) particular tags to an easier form, e.g. '...<span class="acronym">DSSSL</span>...' --> '...<acronym>DSSSL</acronym>...'
    if lang_src == 1:
        html_src = shiftTagsLang1(TAGS_2_SHIFT, html_src)
    if lang_tgt == 1:
        html_tgt = shiftTagsLang1(TAGS_2_SHIFT, html_tgt)
        

    # remove fragments from the list, if one of them doesnt exist in html file
    items2remove_src = getFrags2Remove(html_src, xtargets_src, src_addr, lang_src)
    items2remove_tgt = getFrags2Remove(html_tgt, xtargets_tgt, tgt_addr, lang_tgt)
    if items2remove_src != set([]) or items2remove_tgt != set([]):
        removeFragments(src_addr, tgt_addr, html_src, html_tgt, xtargets_src, xtargets_tgt, items2remove_src, items2remove_tgt)

    # append sentences from one html file to the list of sentences
    #h = open('a_'+src_addr.split('/')[-1],'w')
    #h.write(str(xtargets_src)+'\n'+str(html_src)+'\n'+str(lang_src))
    #h.close()

    #get rid of the sentences into a text file, so that the memory doesn't get full
    if len(xtargets_src) != len(xtargets_tgt): 
        print "Skipping %d sentences because not aligned" % len(xtargets_src)
    else:        
        for sen in xtargets_src: 
            src_sentence = getFragments(sen, html_src, lang_src)
            src_file.write (src_sentence + "\n")
            print "s",
        
        print

        for sen in xtargets_tgt: 
            tgt_sentence = getFragments(sen, html_tgt, lang_tgt)
            tgt_file.write (tgt_sentence + "\n")
            print "t",
        



    


    #srcSentenceList.append(src_sentences)
    #tgtSentenceList.append(tgt_sentences)
    print '\n'
    #h.write('\n')
    
    #if src_addr == 'PHP/php_en/html/features.commandline.html': break
    i = i + 1
    
    #if i == 2:
    #    break
#h.close()



src_file.close()
tgt_file.close()
print i


