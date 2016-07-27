#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 28 Οκτ 2010

@author: Eleftherios Avramidis
"""

import codecs
from StringIO import StringIO
from lxml import etree 
from lxml import objectify 

SCHEMA = StringIO("""\
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:element name="jcml" type="corpus" />
        <xs:complexType name="corpus">
            <xs:sequence>
                <xs:element name="judgedsentence" type="parallelsentence" />
            </xs:sequence>
        </xs:complexType>
        <xs:complexType name="parallelsentence">
            <xs:sequence>
                <xs:element name="src" type="sentence" />
                <xs:element name="tgt" type="sentence" />
                <xs:element name="ref" type="sentence" />
            </xs:sequence>
            <xs:attribute name="id" type="xs:int" /> 
            <xs:attribute name="langsrc" type="xs:string"  />
            <xs:attribute name="langtgt" type="xs:string" />
            <xs:attribute name="rank" type="xs:string" use="optional" />
            <xs:attribute name="testset" type="xs:string" use="optional" />
            <xs:anyAttribute/>
        </xs:complexType>    
        <xs:complexType name="sentence">
            <xs:simpleContent>
              <xs:extension base="xs:string">
                <xs:attribute name="system" type="xs:string" />
              </xs:extension>
            </xs:simpleContent>
        </xs:complexType>
    </xs:schema>
 """)

FILENAME = "../data/evaluations_all.jcml"

class SchemaData(object):
    """
    Imports and directly objectifies the XML input data, based on a Schema description 
    Development suspended as it was not possible to have optional arguments
    """


    def __init__(self):
        """
        Constructor
        """
        schema = etree.XMLSchema(file=SCHEMA)
        parser = objectify.makeparser(schema = schema)
        

        jcml_file = codecs.open(FILENAME, mode='r',  encoding='utf-8')
        jcml = jcml_file.read()
        
        a = objectify.fromstring(jcml, parser)
        
        