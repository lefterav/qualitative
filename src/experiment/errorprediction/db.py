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
from collections import OrderedDict

MYSQL_HOST = 'berlin-188.b.dfki.de'
MYSQL_USER = 'features_fetcher'
MYSQL_PASSWORD = 'dDWyadA3xHQB79yP'
MYSQL_DB = 'featuresR2'
import logging

class DbConnector:
    """
    Class that maintains an open connection with mysql, in order to execute
    consequent queries without having to authenticate again and again
    """
    def __init__(self):
        self.con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,  charset="utf8")
        with self.con:
            self.cur = self.con.cursor()
    
    def fetch_postediting(self, uid, system, source_lang, target_lang):
        """
        Retrieve the post-edited system output for the given sentence id
        """ 
        logging.warn("Trying to retrieve post-editing for sentence_id={}".format(uid))
        query = "SELECT `sentence` FROM `post_edit_all` WHERE `sentence_id`=%s AND {}=1 AND `source_lang`=%s AND `target_lang`=%s".format(system)
        
        self.cur.execute(query, (uid, source_lang, target_lang))
        logging.warn(query % self.con.literal((uid, source_lang, target_lang)))
        try:
            sentence = self.cur.fetchone()[0]
            logging.warn("Found")
            return sentence
        except:
            logging.warn("Not found :(")
            return None
    
    
    def fetch_reference(self, uid, target_lang):
        """
        Retrieve a reference for the given sentence id
        """
        query = "SELECT `source_sentence` FROM `translation_all` WHERE `sentence_id`=%s  AND `source_lang`=%s "
        self.cur.execute(query, (uid, target_lang))
        try:
            sentence = self.cur.fetchone()[0]
            logging.warn("Found")
            return sentence
        except:
            logging.warn("Not found :(")
            return None


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
        
def db_update(table, dbentries, dbfilters):
    con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,  charset="utf8")
    with con:
        cur = con.cursor()
        
        columnquery = ", ".join(["`{}`={}".format(k,v) for k,v in dbentries])
        filterquery = " AND ".join(["`{}`='{}'".format(k,v) for k,v in dbfilters])
        
        query = "UPDATE `{}`.`{}` SET {} WHERE {}".format(MYSQL_DB, table, columnquery, filterquery)

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


def retrieve_manual_error_classification(uid):
    pass



def retrieve_auto_error_classification(uid, system, testset, source_lang, target_lang):
    con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,  charset="utf8")
    with con:
        #fetch all sentences and their languages
        cur = con.cursor()
        query = """SELECT  `Wer` ,  `Rper` ,  `Hper` ,  `rINFer` ,  `hINFer` ,  `rRer` ,  `hRer` ,  `MISer` ,  `EXTer` ,  `rLEXer` , `hLEXer` ,  `brINFer` ,  `bhINFer` ,  `brRer` ,  `bhRer` ,  `bMISer` ,  `bEXTer` ,  `brLEXer` ,  `bhLEXer`  
                    FROM  `auto_error_classification`  
                    WHERE `sentence_id` = %s
                    AND `system` = %s
                    AND `testset` = %s
                    AND `source_lang` = %s
                    AND `target_lang` = %s
                    """
        cur.execute(query, (uid, system, testset, source_lang, target_lang))
        result = cur.fetchone()
        desc = [item[0] for item in cur.description]
        
        results = OrderedDict([(key, int(value)) for key, value in zip(desc, result)])
        
    return results
    
    

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
#    print retrieve_auto_error_classification('wmt10-idnes.cz/2009/12/10/74900-1', 'moses', 'wmt', 'de', 'en')
    c = DbConnector()
    print c.db_fetch_postediting("069592001_cust1-069592001-1", "moses", "de", "en")
    
        
