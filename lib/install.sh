echo "Downloading required java libraries. Please be patient..."
wget http://www.dfki.de/~elav01/download/qualitative/lib/BerkeleyParser.jar
#wget https://berkeleyparser.googlecode.com/files/BerkeleyParser-1.7.jar
wget http://www.dfki.de/~elav01/download/qualitative/lib/LanguageTool.jar
wget http://www.dfki.de/~elav01/download/qualitative/lib/meteor-1.3.jar
wget http://www.dfki.de/~elav01/download/qualitative/lib/py4j0.7.jar
echo "Done. Compiling necessary java code of ours..."
javac -cp py4j0.7.jar ../src/util/JavaServer.java -d .
javac -cp ./BerkeleyParser.jar ../src/featuregenerator/parser/berkeley/socket/BParser.java -d .
echo "Done. Now is time to download the necessary resources (probably by running the script into the directory /res) ."