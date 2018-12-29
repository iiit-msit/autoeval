import subprocess, sys
import datetime
from dateutil.tz import tzlocal
import os
from io import StringIO

def add_row(row):
	if not os.path.exists('logs'):
		os.makedirs('logs')

	if not os.path.exists('logs/log.csv'):
		f = open("logs/log.csv","w+")
		f.write('timestamp,error_type,error_description\n')
		f.close()

	with open('logs/log.csv','a') as fd:
		fd.write(row['timestamp']+','+row['error_type']+','+row['error_description']+'\n')

stderr = ""
with subprocess.Popen(['python', sys.argv[1]], stderr=subprocess.PIPE, bufsize=1, universal_newlines=True) as p, StringIO() as buf:
	for line in p.stderr:
		print(line, end='')
		buf.write(line)
	stderr = buf.getvalue().rstrip()

row = {}
now = datetime.datetime.now()
now_str = now.strftime('%Y-%m-%d %H:%M:%S %Z')

if len(stderr) != 0:
	row['timestamp'] = now_str
	row['error_type'] = stderr.split('\n')[-1].rstrip().split(':')[0]
	row['error_description'] = stderr.split('\n')[-1].rstrip().split(':')[1]
	add_row(row)
