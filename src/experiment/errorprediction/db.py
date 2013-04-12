#!/usr/bin/python
# -*- coding: utf-8

'''
Provides syncing support for IDs stored in a MySQL db

Created on 11 Apr 2013


@author: Eleftherios Avramidis
'''

import MySQLdb as mdb
import sys

MYSQL_HOST = 'localhost'
MYSQL_USER = 'features_fetcher'
MYSQL_PASSWORD = 'dDWyadA3xHQB79yP'
MYSQL_DB = 'featuresR2'



def db_add_entries(dbentries, table):
    """
    Receive a list of tuples (column, value) and insert them to the specified mysql table
    """
    
    con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
    
    with con:
        cur = con.cursor()
        for dbentry in dbentries:
            cols = []
            values = [] 
            for col, value in dbentry:
                cols.append(col)
                values.append("'{}'".format(value))
            colquery = ",".join(cols)
            valquery = ",".join(values)
                        
            cur.execute("INSERT INTO %s (%s) VALUES (%s)", table, colquery, valquery)
            print ">",
            

def retrieve_uid(source_sentence, previous_ids=[], filters=[]):
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
    
    con = None
    source_sentence = source_sentence.strip()
    filterquery = ''
    
    if filters:
        filterstring = " AND ".join(["{} = '{}'".format(col, val) for col,val in filters]) 
        filterquery = "AND {}".format(filterstring)
    
    try:
        con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
        cur = con.cursor()
        if previous_ids:
            print "SELECT sentence_id FROM translation_all WHERE source_sentence LIKE '%s' AND sentence_id NOT IN %s {} ORDER BY id".format(filterquery) % (source_sentence, ",".join(previous_ids))
            cur.execute("SELECT sentence_id FROM translation_all WHERE source_sentence LIKE %s AND sentence_id NOT IN %s {} ORDER BY id".format(filterquery), (source_sentence, ",".join(previous_ids)))
        else:
            print "SELECT sentence_id FROM translation_all WHERE source_sentence LIKE '%s' {} ORDER BY id".format(filterquery) % (source_sentence)
            cur.execute("SELECT sentence_id FROM translation_all WHERE source_sentence LIKE %s {} ORDER BY id".format(filterquery), (source_sentence))
            
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
        print "<",
        return uid
    except:
        print "v",
        return None
    
if __name__ == '__main__':
    print retrieve_uid("%Barack Obama%")
        