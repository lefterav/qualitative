# -*- coding: utf-8 -*-
__author__ = "Christian Federmann <cfedermann@dfki.de>"
import re
import sys
import xml.etree.cElementTree as CT
from datetime import datetime


class BaseTree(object):
    """ This class defines the basic structure, attributes and methods for
    Lucy parse trees.  It provides a parser and creates a cElementTree from
    the given text.  Both the tree and the list representation of the parsed
    text are available to the class user.
    """
    __code__ = []
    __attr__ = []
    __tags__ = []
    __list__ = []
    __tree__ = None
    __debug_tree__ = False
    
    def __init__(self, text, attr, code):
        """ This method initializes a new BaseTree sub-class object.  The text
        parameter specifies the text content which should be parsed, the attr
        dictionary allows to specify one or several features that should be
        extracted from parsed data chunks.  The code parameter tells the class
        the name of the XML base container for the resulting cElementTree.
        """
        __start = datetime.now()
        self.__code__ = code
        self.__attr__ = attr
        self.dct = {}
        self.dct['max-tree-depth'] = 0
        self.dct['nodes-total'] = 0
        self.dct['leaves-total'] = 0
        self.__parse_text__(BaseTree.__cleanup__(text))
        #self.__build_tree__()
        __end = datetime.now()
        
        if self.__debug_tree__:
            print "[ start: %r ]" % __start
            print "[ end: %r ]" % __end
            print "[ duration: %r ]" % str(__end-__start)
    
    
    def __build_tree__(self):
        """ Builds an ElementTree from the internal tree list representation.
        Do NOT call this method directly, the __init__ method does already!
        """
        root = CT.Element(self.__code__)
        root.attrib['depth'] = "0"
        root.attrib['range'] = "(0, 0)"
        parents = [root]
        
        _position = 0

        for index in xrange(len(self.__list__)):
            values = self.__list__[index]
            
            # Check whether the list element contains a category value.
            if values[1]:
                while values[0] <= int(parents[-1].attrib['depth']):
                    node = parents.pop()
                    
                    # Update range information for deleted node.
                    range_data = eval(node.attrib['range'])
                    node.attrib['range'] = str((range_data[0], _position))
                
                # Check whether the current node is a child or sibling.
                if index > 1 and values[0] <= self.__list__[index-1][0]:
                    _position += 1
                
                # Update range information for current parent node.
                node = parents[-1]
                range_data = eval(node.attrib['range'])
                node.attrib['range'] = str((range_data[0], _position))
                
                # Construct a new node and add it to the tree.
                node = CT.SubElement(parents[-1], values[1])
                node.set('depth', str(values[0]))
                node.set('range', str((_position, _position)))
                
                # Append new node to list of parents as it may have children.
                parents.append(node)
                
                # If additional attributes are given, add them to the node.
                if len(values) > 3:
                    for key, value in values[3].items():
                        node.set(key, value)
            
            else:
                node = parents[-1]
                while int(node.attrib['depth']) > values[0] + 1:
                    node = parents.pop()
                    
                    # Update range information for deleted node.
                    range_data = eval(node.attrib['range'])
                    node.attrib['range'] = str((range_data[0], _position))
                
                # Fix to prevent failure for degenerated Lucy data.
                if not len(parents):
                    raise AssertionError('parents should never be empty!')

        # Fix range attribute for root element.
        root.attrib['range'] = str((0, _position))
        self.__tree__ = CT.ElementTree(root)
    
    
    @staticmethod
    def __cleanup__(text):
        """ Takes a given text and normalizes whitespaces.  This will replace
        all sequences of whitespace characters by a single space character.
        """
        spaces = re.compile("\s+")
        return spaces.sub(" ", text)
    
        
    def __indent__(self, element, level=0):
        """ Helper method that takes an ElementTree and prepares it for pretty
        printing by adding indenting whitespace to the nodes' .tail attribute.

        Adapted from source code by Filip Salomonsson available at:
        - http://infix.se/2007/02/06/gentlemen-indent-your-xml
        """
        _indent = "\n{0}".format("  " * level)
        if len(element):
            if not element.text or not element.text.strip():
                element.text = "{0}  ".format(_indent)
            
            for child in element:
                self.__indent__(child, level+1)
                if not child.tail or not child.tail.strip():
                    child.tail = "{0}  ".format(_indent)
            
            # What exactly are we doing here?
            if not child.tail or not child.tail.strip():
                child.tail = _indent
        
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = _indent
    
    
    def __parse_text__(self, text):
        """ Takes a given text and parses the structure into a list.  Do NOT
        call this method directly, the __init__ method does already!
        """
        self.__list__ = []
        self.__tags__ = []
        
        # We start at depth -1 as we want our depth to be starting at 0.
        depth = -1
        last = 0
        _in_string = False
        
        # Add a leading and a trailing space to ease computation.
        text = " %s " % text
        
        relativeDepth = 0
        for index in xrange(len(text)):
            # Check whether we are entering/exiting String mode.
            if text[index] == '"' and text[index-1] != '\\':
                _in_string = not _in_string
                continue
            
            if not _in_string:
                if text[index] == '(':
                    depth += 1
                    last = index
                    self.dct['nodes-total'] += 1
                    relativeDepth += 1
                
                elif text[index] == ')':
                    chunk = text[last+1:index].strip()
                    depth -= 1
                    last = index
                    
                    if len(chunk):
                        # All Lucy tree nodes should include a category!
                        pattern = re.compile(r"CAT ([A-Z\-$]+)")
                        match = pattern.search(chunk)
                        
                        if match:
                            category = match.group(1)
                            wordField = re.search(r'ALO "([^"]+)"', chunk)
                            if not category in self.__tags__:
                                self.__tags__.append(category)
                                self.save_features(category, depth, relativeDepth, wordField)
                            
                            items = [depth+1, category, chunk]
                            attributes = {}
                                                        
                            for key, values in self.__attr__.items():
                                for value in values:
                                    pattern = re.compile(value)
                                    match = pattern.search(chunk)
                                    if match:
                                        _match = match.group(1)
                                        
                                        # fix double quoted strings.
                                        _p = _match.find('"')
                                        while _p > 0 and _match[_p-1] == '\\':
                                            _p = _match.find('"', _p+1)

                                        if _p > -1:
                                            _match = _match[:_p]
                                        
                                        _match = _match.replace('\\"', '"')
                                        attributes[key] = _match
                                        break
                            
                            items.append(attributes)
                            self.__list__.append(tuple(items))
                        
                        else:
                            relativeDepth = 0
                            continue
                        relativeDepth = 0
                    
                    else:
                        # Only add a "closing" list entry if the next symbol
                        # is NOT an opening parenthesis!  Ignore any spaces.
                        i = 1
                        while index+i < len(text)-1 and text[index+i] == ' ':
                            i += 1
                        
                        if index+i < len(text)-1 and text[index+i] != '(':
                            self.__list__.append((depth+1, None))


    def __raw__(self, node):
        """ Takes the given ElementTree node and returns the corresponding raw
        text that decribed the node in the original Lucy data.  Raises the
        AttributeError exception if the node cannot be identified in the
        __list__ variable of the BaseTree instance.
        """
        depth = int(node.attrib["depth"])
        category = node.tag
        
        candidates = filter(lambda x: x[0] == depth and x[1] == category,
          self.__list__)

        for candidate in candidates:
            found = True
            for key in self.__attr__.keys():
                if not candidate[3].has_key(key) or \
                    candidate[3][key] != node.attrib[key]:
                    found = False
                    break
            
            if found:
                return candidate[2]

        raise AttributeError

    
    def attributes(self, node):
        """ Takes the given ElementTree node and returns the attributes that
        are attached to this exact node.  Data is returned as a tuple which
        contains the element tag and all attributes values.
        """
        return (node.tag, node.attrib)
    

    def save_features(self, category, depth, relativeDepth, wordField):
        if not '%s-total'%category in self.dct.keys():
            self.dct['%s-depth-absolute'%(category)] = depth+1
            self.dct['%s-depth-relative'%(category)] = relativeDepth-1
            if wordField:
                count = wordField.group(1).count(' ')+1
                self.dct['%s-words-total'%(category)] = count
            self.dct['%s-total'%(category)] = 1

            self.dct['leaves-total'] += 1                                
            if depth+1 > self.dct['max-tree-depth']:
                self.dct['max-tree-depth'] = depth+1
        else:
            self.dct['%s-depth-absolute'%(category)] = float(self.dct['%s-depth-absolute'%(category)]*self.dct['%s-total'%(category)]+depth+1)/(self.dct['%s-total'%(category)]+1)
            
            self.dct['%s-depth-relative'%(category)] = float(self.dct['%s-depth-relative'%(category)]*self.dct['%s-total'%(category)]+relativeDepth-1)/(self.dct['%s-total'%(category)]+1)

            if wordField:
                count = wordField.group(1).count(' ')+1
                self.dct['%s-words-total'%(category)] = float(self.dct['%s-words-total'%(category)]*self.dct['%s-total'%(category)]+count)/(self.dct['%s-total'%(category)]+1)

            if depth+1 > self.dct['max-tree-depth']:
                self.dct['max-tree-depth'] = depth+1
            self.dct['%s-total'%(category)] += 1


    def contains(self, node, child):
        """ Takes two nodes from the underlying ElementTree and checks whether
        node contains the given child, i.e. whether child is contained within
        the sub tree spanned by node.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")
        
        if node == child:
            return True
        
        return any([self.contains(x, child) for x in node.getchildren()])
    
    
    def elements(self, tag):
        """ Extracts elements from the underlying ElementTree that match the
        given tag parameter.  Elements are ordered by increasing size which
        means that "shorter" elements, i.e. elements that have a less leaves
        will be put before "larger" elements which have more leaves attached.
        Raises a ValueError if an unknown tag is requested.
        """
        if not tag in self.__tags__:
            raise ValueError("unknown tag %r cannot be used!" % tag)
        
        elements = self.__tree__.getroot().findall("*//%s" % tag)
        
        # Sort the found elements by increasing element size, if element size
        # is equal, order by increasing terminal positions.
        def _cmp(x, y):
            result = self.size(x)-self.size(y)
            if result == 0:
                _xrange = eval(x.attrib['range'])
                _yrange = eval(y.attrib['range'])
                result = _xrange[0]-_yrange[0]
            
            return result
        
        elements.sort(cmp=_cmp)
        
        return elements


    def substitute(self, node, nodes, attr):
        """ Takes the given ElementTree node and computes the text which can
        be extracted from the leaves.  The attr list specifies which of the
        attributes of the node should generate the text.  If no such value is
        given, the empty String will be used as a fallback value.  The given
        dictionary nodes may contain text that should be used instead of the
        text contained in the spanned sub tree.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")

        _text = []
        for child in node.getchildren():
            if child in nodes.keys():
                child_text = self.text(child).replace('<EMPTY>', '').strip()
                _text.append((child_text, nodes[child]))
            else:
                if not len(child.getchildren()):
                    _value = ''
                    if child.attrib.has_key(attr):
                        _value = child.attrib[attr]
                    
                    _text.append(_value)
                
                else:
                    _text.extend(self.substitute(child, nodes, attr))
        
        return _text
    
    
    def subtree(self, node):
        """ Takes the given ElementTree node and returns the data attached to
        the all nodes from the spanned sub tree.  Data is put into tuples
        containing the element tag and all other attributes that can be
        extracted from the respective element.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")
        
        # First, we collect all attributes from the current node.        
        _data = [(node.tag, node.attrib)]
        
        # Then, we handle child nodes...        
        for child in node.getchildren():
            _data.extend(self.subtree(child))
        
        return _data


    def size(self, node):
        """ Takes the given ElementTree node and returns the number of leaves
        that can be found within the spanned sub tree.
        """
        return len(self.terminals(node))


    def get_root(self):
        """ Returns the root of this ElementTree. """
        return self.__tree__.getroot()

    
    def terminals(self, node):
        """ Takes the given ElementTree node and returns the data attached to
        the leaves.  Data is put into tuples containing the element tag and
        all other attributes that can be extracted from the element.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")
        
        _data = []
        for child in node.getchildren():
            if not len(child.getchildren()):
                _data.append((child.tag, child.attrib))
            
            else:
                _data.extend(self.terminals(child))
        
        return _data

    def pos_tags(self, node):
        """ Takes the given ElementTree node and returns the data attached to
        the leaves.  Data is put into tuples containing the element tag and
        the lemma that can be extracted from the element.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")

        _data = []
        for child in node.getchildren():
            if not len(child.getchildren()):
                try:
                    _surface = child.attrib['surface']
                    _lemma = child.attrib['lemma']
                    _data.append((_surface, child.tag, _lemma))
                except:
                    _data.append((child.tag, 'NULL'))

            else:
                _data.extend(self.pos_tags(child))

        return _data
    
    
    def tags(self, node):
        """ Takes the given ElementTree node and returns the list of all tags
        attached to the nodes from the spanned sub tree.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")
        
        # First, we collect the tag from the current node.        
        _data = [node.tag]
        
        # Then, we handle child nodes...        
        for child in node.getchildren():
            _data.extend(self.tags(child))
        
        return _data

    
    def text(self, node, attr=()):
        """ Takes the given ElementTree node and computes the text which can
        be extracted from the leaves.  The attr list specifies which of the
        attributes of the node should generate the text.  If no such value is
        given, the <EMPTY> placeholder will be used as a fallback value.
        """
        if not hasattr(node, "getchildren"):
            raise ValueError("node has to export method getchildren().")
        
        _text = []
        for child in node.getchildren():
            if not len(child.getchildren()):
                _value = None
                for _attr in attr:
                    if child.attrib.has_key(_attr):
                        _value = child.attrib[_attr]
                        break
                
                if not _value:
                    _value = "<EMPTY>"
                
                _text.append(_value)
            
            else:
                _text.append(self.text(child, attr))
        
        return " ".join(_text)
    
    
    def pretty_print(self):
        """ Pretty-prints the XML structure of the underlying cElementTree.
        Uses the __indent__() helper method defined above.
        """
        self.__indent__(self.__tree__.getroot())
        self.__tree__.write(sys.stdout)


class AnalysisTree(BaseTree):
    """ This class allows to create a tree representation from a given text
    String that contains Lucy analysis data.  Based on the BaseTree code.
    """
    def __init__(self, text):
        """ This method initializes a new AnalysisTree object.  The required
        parameter text is a text String which contains Lucy analysis data.
        """
        __params__ = {
          'lemma': (r'CAN "(.*)"',),
          'surface': (r'ALO "(.*)"',)
        }
        super(AnalysisTree, self).__init__(text, __params__, 'ANALYSIS')
    
    
    def text(self, node, attr=('surface',)):
        """ Takes the given ElementTree node and computes the text which can
        be extracted from the leaves.  For the AnalysisTree, we compute the
        text from the surface attribute iff available.
        """
        return super(AnalysisTree, self).text(node, attr)


class TransferTree(BaseTree):
    """ This class allows to create a tree representation from a given text
    String that contains Lucy transfer data.  Based on the BaseTree code.
    """
    def __init__(self, text):
        """ This method initializes a new TransferTree object.  The required
        parameter text is a text String which contains Lucy transfer data.
        """
        __params__ = {
          'source': (r'(?:SL-CAN) "(.*)"', r'(?:^[^-]?CAN) "(.*)"'),
          'target': (r'TL-CAN "(.*)"',)
        }
        super(TransferTree, self).__init__(text, __params__, 'TRANSFER')
    
    
    def text(self, node, attr=('target', 'source')):
        """ Takes the given ElementTree node and computes the text which can
        be extracted from the leaves.  For the TransferTree, we compute the
        text from the target attribute or from the source attribute if only
        that is available.
        """
        return super(TransferTree, self).text(node, attr)


class GenerationTree(BaseTree):
    """ This class allows to create a tree representation from a given text
    String that contains Lucy generation data.  Based on the BaseTree code.
    """
    def __init__(self, text):
        """ This method initializes a new GenerationTree object.  The required
        parameter text is a text String which contains Lucy generation data.
        """
        __params__ = {
          'lemma': (r'CAN "(.*)"',),      
          'surface': (r'ALO "(.*)"',)
        }
        super(GenerationTree, self).__init__(text, __params__, 'GENERATION')
    
    
    def text(self, node, attr=('surface',)):
        """ Takes the given ElementTree node and computes the text which can
        be extracted from the leaves.  For the GenerationTree, we compute the
        text from the surface attribute iff available.
        """
        return super(GenerationTree, self).text(node, attr)

