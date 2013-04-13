#!/usr/bin/python
# -*- coding: utf-8

'''
Provides syncing support for IDs stored in a MySQL db

Created on 11 Apr 2013


@author: Eleftherios Avramidis
'''

import MySQLdb as mdb
import sys
import cgi

MYSQL_HOST = 'berlin-188.b.dfki.de'
MYSQL_USER = 'features_fetcher'
MYSQL_PASSWORD = 'dDWyadA3xHQB79yP'
MYSQL_DB = 'featuresR2'



def db_add_entries(dbentries, table):
    """
    Receive a list of tuples (column, value) and insert them to the specified mysql table
    """
    
    con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,  charset="utf8")
    
    with con:
        cur = con.cursor()
        for dbentry in dbentries:
            cols = []
            values = [] 
            for col, value in dbentry:
                cols.append(col)
                values.append("{}".format(value))
            colquery = ",".join(cols)
            valquery = "','".join(values)
                        
            query = "INSERT INTO `{}` ({}) VALUES ('{}')".format(table, colquery, valquery)
            print query
            cur.execute(query)
            
            print ">",
        
def db_update(table, dbentry, dbfilter):
    con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,  charset="utf8")
    with con:
        cur = con.cursor()
        query = "UPDATE `featuresR2`.`{}` SET `{}` = {} WHERE `{}` = {}".format(table, dbentry[0], dbfilter[0], dbfilter[1])
        cur.execute(query)
        print ".",
    
    
def db_add_tokenized_sources():
    con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,  charset="utf8")
    
    from featuregenerator.preprocessor import Tokenizer
    import HTMLParser
    
    htmlparser = HTMLParser.HTMLParser()
    
    with con:
        #fetch all sentences and their languages
        cur = con.cursor()
        query = "SELECT `id`, `source_sentence`, `source_lang` FROM `translation_all` ORDER BY `id`,`source_lang`"
        cur.execute(query)
        
        tokenizer = None
        
        for sid, source_sentence, source_lang in cur.fetchall():
            
            #load the tokenizer if needed
            if not tokenizer or tokenizer.lang != source_lang:
                tokenizer = Tokenizer(source_lang)
                
            escaped_sentence = htmlparser.unescape(source_sentence)
            processed_sentence = tokenizer.process_string(escaped_sentence)
            #reescaped_sentence = htmlparser.unescape(processed_sentence)
            
            query = "UPDATE `featuresR2`.`translation_all` SET `source_sentence_tok` = %s WHERE `translation_all`.`id` = %s"
            cur.execute(query, (processed_sentence, sid))
        

def retrieve_uid(source_sentence, previous_ids=[], filters=[], **kwargs):
    """
    Retrieve the unique id of the sentence from the database, 
    or return fals
    @param sentence: a source sentence that will be looked up in the db
    @type sentence: str
    @param previous_ids: make sure that the same uid is not returned twice
    @param filters: a list of tuples of (column, value) for filtering based on columns
    @type filters: tuple(str, str)
    @return: the unique ID of the sentence or False
    @rtype: str or None 
    """
    
    tokenized = kwargs.setdefault("tokenized", True)    
    
    if tokenized: 
        table = "source_sentence_tok"
    else:
        table = "source_sentence"
    
    con = None
#    print source_sentence
    unprocessed_sentence = source_sentence
    source_sentence = source_sentence.strip()
#    print source_sentence
    
    filterquery = ''
    
    if filters:
        filterstring = " AND ".join(["{} = '{}'".format(col, val) for col,val in filters]) 
        filterquery = "AND {}".format(filterstring)
    
    
    try:
        con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, charset="utf8")
        cur = con.cursor()
        if previous_ids:
            query = "SELECT sentence_id FROM translation_all WHERE {} LIKE %s AND sentence_id NOT IN ('{}') {} ORDER BY id".format(table, "','".join(previous_ids), filterquery)
            params = source_sentence  
        else:
            query = "SELECT sentence_id FROM translation_all WHERE {} LIKE %s {} ORDER BY id".format(table, filterquery)
            params = source_sentence
            
        cur.execute(query, params)
        uid = cur.fetchone()
#        print uid
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:    
        if con:    
            con.close()
    
    try:
        uid = uid[0]
#        print "<",
        return uid
    except:
        print
        print "v",
        print unprocessed_sentence
        print source_sentence
        print query
        return None
    
if __name__ == '__main__':
    db_add_tokenized_sources()
        