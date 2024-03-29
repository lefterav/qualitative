In order to run the program please follow the steps:

0. Add the /src directory into the PYTHONPATH of your linux 
   Debian/Ubuntu: export PYTHONPATH = $PYTHONPATH:/home/<dirname>/qualitative/src
1. Install python requirements and external programs (see below)
2. Change directory to /lib and run "bash install.sh" to download Java libraries
3. Download linguistic resources (suggested folder in /res; there may be a bash script to do that)
4. Specify the location of the linguistic resources to the configuration files
5. To test installation start the LM server and run src/app/autoranking/application.py <classifier_file> <annotation.config.1> [<annotation.config.2> ...]


============
Requirements
============

This is a list of the requirements for running the suite. Please scroll
for more hints on their installation

For Debian/ubuntu:

#install java
sudo apt-add-repository ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install openjdk-8-jdk


#install python libraries

sudo apt-get install python-dev g++ build-essential python-pip libblas-dev liblapack-dev gfortran

sudo pip install --upgrade pip  

sudo pip install <package-name>

or for user-specific installation (no root or 
not wanting to risk your python environment) 
 pip install --user <package-name> 

pip install setuptools
pip install nltk==2.0.5
easy_install -U distribute
pip install -r requirements.txt
pip install https://github.com/kpu/kenlm/archive/master.zip 
 
#  nltk==2.0.1rc4 and matplotlib need to be checked

Additionally
* expsuite [only for training] (Manually from https://github.com/lefterav/expsuite)

external programs [need to start separately]
* lmserver wrapped over SRILM [soon to be replaced by KenLM]
* Acrolinx IQ [proprietary-optional]

jar files (automatically fetched by "cd lib; bash install.sh")
* py4j
* Berkeley parser
* Meteor
* Language tool 

other resources (automatically fetched by "cd res; bash download.sh":
* language model for source and target language (ARPA format)
* trained grammar for Berkeley parser (source and target language)
* truecaser model for source and target language (see Moses)
* pre-trained quality estimation ranking model


Orange ML toolkit
--------------------
sudo apt-get install python-dev g++ build-essential python-pip 
sudo pip install --upgrade pip  
sudo pip install orange

* There is also a debian package / repository called orangesvn ( sudo apt-get install orangesvn) but works only with python 2.5. If you use it, you may have to tackle pythonpath issues

No root access:
- Go to http://orange.biolab.si/ and download packed sources
- python setup.py install --user



Other platforms


Use the standard way to install pip at your operating system or get pip from here: 
http://pypi.python.org/pypi/pip

pip install orange


Various other libraries
-------
sudo apt-get install python-nltk (in Ubuntu 10.04 or later) otherwise try with pip  

	sudo apt-get install libyaml-dev
	sudo pip install nltk

sudo apt-get remove python-numpy python-scipy (repositories provide only old versions)
sudo apt-get install python python-dev gcc gfortran g++ libblas-dev libatlas-cpp-0.6-dev liblapack-dev libblas-dev libsuitesparse-dev   
sudo pip install numpy
sudo pip install scipy 



ruffus :
----------

Ruffus is a pipeline execution framework for Python, that is used for the preprocessing of the data in scripts such as src/exexperiment/autoranking/annotate_updated. If you already have annotated data you can skip this

Ruffus can be installed also by using pip install. If you have problems check the following:

wget http://launchpadlibrarian.net/11726755/pypy-lib_1.0.0-svn51091-1_all.deb
wget https://launchpad.net/ubuntu/+source/pypy/1.0.0-svn51091-1/+build/503581/+files/pypy_1.0.0-svn51091-1_amd64.deb
wget https://launchpad.net/ubuntu/+source/pypy/1.0.0-svn51091-1/+build/503581/+files/pypy-stackless_1.0.0-svn51091-1_amd64.deb
dpkg -i 


Python ExpSuite
---------------
Expsuite is a set of scripts that parallelizes the training of a big numbers of systems, with various parameters, and allows monitoring the results. Please check out the latest version of expsuite and add it to the python path

https://github.com/lefterav/expsuite

Check out -
