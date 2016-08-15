echo "This is an experimental script downloading resources"
cd grammars
wget https://berkeleyparser.googlecode.com/files/eng_sm6.gr
wget https://berkeleyparser.googlecode.com/files/ger_sm5.gr
cd ..
cd lms
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/news.3gram.de.lm
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/news.3gram.en.lm
cd ..
cd trucasers
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/truecase-model.3.de
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/truecase-model.3.en
cd ..
cd qe
wget http://www.qt21.eu/software/qualitative/res/qe/classifier.de-en.clsf
cd ..
mkdir -p ibm1
cd ibm1
wget http://www.qt21.eu/software/qualitative/res/ibm1/lex.cs-en.tar.gz
wget http://www.qt21.eu/software/qualitative/res/ibm1/lex.de-en.tar.gz
wget http://www.qt21.eu/software/qualitative/res/ibm1/lex.es-en.tar.gz
wget http://www.qt21.eu/software/qualitative/res/ibm1/lex.fr-en.tar.gz
tar xzf *gz
rm *gz
cd ..

echo "Resources downloaded. Please modify the necessary "annotation*.cfg" configuration file(s) and pass it as parameter to app/autoranking/application.py for testing"
