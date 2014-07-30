echo "This is an experimental script downloading resources for German-English"
wget https://berkeleyparser.googlecode.com/files/eng_sm6.gr
wget https://berkeleyparser.googlecode.com/files/ger_sm5.gr
mv *gr grammars/
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/news.3gram.de.lm
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/news.3gram.en.lm
mv *lm lms/
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/truecase-model.3.de
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/truecase-model.3.en
mv *truecase* trucasers/
wget http://www.qt21.eu/software/qualitative/res/qe/classifier.de-en.clsf
mv classifier.de-en.clsf qe/
echo "Resources downloaded. Please modify the necessary "annotation*.cfg" configuration file(s) and pass it as parameter to app/autoranking/application.py for testing"