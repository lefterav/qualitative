JAVA_PATH=/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/
echo "Downloading required java libraries. Please be patient..."
wget http://www.dfki.de/~elav01/download/qualitative/lib/BerkeleyParser.jar
#wget https://berkeleyparser.googlecode.com/files/BerkeleyParser-1.7.jar
wget https://languagetool.org/download/LanguageTool-3.2.zip
unzip LanguageTool-3.2.zip
rm LanguageTool-3.2.zip
wget http://www.dfki.de/~elav01/download/qualitative/lib/meteor-1.3.jar
wget http://central.maven.org/maven2/net/sf/py4j/py4j/0.9.2/py4j-0.9.2.jar
echo "Done. Compiling necessary java code of ours..."
$JAVA_PATH/javac -cp py4j-0.9.2.jar ../src/util/JavaServer.java -d .
$JAVA_PATH/javac -cp ./BerkeleyParser.jar ../src/featuregenerator/blackbox/parser/berkeley/socketservice/BParser.java -d .
echo "Done. Now is time to download the necessary resources (probably by running the script into the directory /res) ."
