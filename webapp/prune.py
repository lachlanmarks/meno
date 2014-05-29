#this script is executed as root via a cronjob every hour on the hour (server time = Melb time)
#look at the script by typing 'crontab -e' as root. 
#the line is: 0 * * * cd /home/webapp && python prune.py


###########################################
#PRUNE.PY: deletes all session files that # 
#          have not been modified in the  #
#	   last 30 minutes		  #
###########################################


import os, time

session_dir = '/tmp/'

def last_modded(f):
	t = os.path.getmtime(session_dir + f)
	return t
	
file_list = os.listdir(session_dir)
now = time.time()

for f in file_list:
	if 'werkzeug' in f and last_modded(f) < (now - 1800):
		os.unlink(session_dir + f)

