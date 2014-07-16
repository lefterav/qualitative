wget https://berkeleyparser.googlecode.com/files/eng_sm6.gr
wget https://berkeleyparser.googlecode.com/files/ger_sm5.gr
wget https://berkeleyparser.googlecode.com/files/fra_sm5.gr
mv *gr grammars/
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/news.3gram.de.lm
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/news.3gram.en.lm
mv *lm lms/
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/truecase-model.3.de
wget http://www.quest.dcs.shef.ac.uk/quest_files/de-en/truecase-model.3.en
mv *truecase* trucasers/
