

#####################
Starting the services
#####################

1. Setting up environment (TODO: automate)

ssh -l<username> <servername>
sudo -sHu lt-mts
cd /project/qtleap/software/selection_mechanism/qualitative/src/app/hybrid/servers/
source /project/qtleap/software/virtual_environments/qualitative_14.04/bin/activate
export PYTHONPATH=$PYTHONPATH:/project/qtleap/software/selection_mechanism/qualitative/src/
script /dev/null
screen
# now run the following commands in the commandline
# press Ctrl+A+D to leave the screen running in the back ground


2. Start Moses pilot1 en-de at lns-87247.dfki.uni-sb.de

bash /project/qtleap/software/mtmonkey/user/en-de/mt-2.1/scripts/run_moses
python xmlrpcserver_worker.py --host lns-87247.dfki.uni-sb.de --port 9200 --uri http://lns-87247.dfki.uni-sb.de:9202 --source_language en --target_language de --truecaser_model /project/qtleap/pilot0/systems/de-en/truecaser/truecase-model.2.en  --splitter_model /project/qtleap/pilot0/systems/de-en/splitter/split-model.2.en


3. Start Moses pilot 1 de-en at lns-87257.dfki.uni-sb.de

bash /project/qtleap/software/mtmonkey/user/en-de/mt-2.1/scripts/run_moses
python xmlrpcserver_worker.py --host lns-87247.dfki.uni-sb.de --port 9300 --uri http://lns-87247.dfki.uni-sb.de:9302 --source_language en --target_language de --truecaser_model /project/qtleap/pilot0/systems/de-en/truecaser/truecase-model.2.en

4. Start Neural Monkey en-de at blade-1.dfki.uni-sb.de

#start Neural Monkey @ blade-1:9502


5. Re-configure appserver (optionally) at blade-3.dfki.uni-sb.de

#edit /project/qtleap/software/mtmonkey-master-2015-03-23/appserver/config/appserver.cfg 
#kill running instance of appserver
ps -ef | grep apps[e]rver.py | awk '{print $2}' | xargs kill
#cron will restart it after a minute


6. Test the running server from any machine:

curl -H "Content-Type: application/json" -X POST -d '{ "action":"translate", "sourceLang":"en", targetLang":"de", "text": "How can I install Windows?", "systemId":"pilot3" }' http://blade-3.dfki.uni-sb.de:8100/translate
