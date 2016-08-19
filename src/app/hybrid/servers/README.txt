#commands to start moses XMLRPC wrapper in DFKI servers
ssh -l<username> lns-87247
sudo -sHu lt-mts
cd /project/qtleap/software/selection_mechanism/qualitative/src/app/hybrid/servers/
source /project/qtleap/software/virtual_environments/qualitative_14.04/bin/activate
script /dev/null
screen 
python xmlrpcserver_moses.py --host lns-87247.dfki.uni-sb.de --port 9200 --uri http://lns-87247.dfki.uni-sb.de:9302 --source_language en --target_language de --truecaser_model /project/qtleap/pilot0/systems/de-en/truecaser/truecase-model.2.en  --splitter_model /project/qtleap/pilot0/systems/de-en/splitter/split-model.2.en
ctrl+A+D
screen
python xmlrpcserver_moses.py --host lns-87247.dfki.uni-sb.de --port 9200 --uri http://lns-87247.dfki.uni-sb.de:9302 --source_language en --target_language de --truecaser_model /project/qtleap/pilot0/systems/de-en/truecaser/truecase-model.2.en
ctrl+A+D
