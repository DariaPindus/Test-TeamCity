import csv
import re
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
import json

EMAIL_FILES_CONFIG_FILE="email_receivers.json"
CHANGED_FILES_TC_PATH="%system.teamcity.build.changedFiles.file%"		#"%system.teamcity.build.changedFiles.file%"
CHANGED_FILES_PATH="changelog.txt"
CHANGED_FILES_INFO_SEPARATOR=":"
CHANGE_TYPE_PROPERTY_NAME="changeType"
JSON_EMAIL_PROP_NAME="email"
JSON_FILE_PROP_NAME="files"
EMAIL_STRUCT_EMAIL_KEY="email"
EMAIL_STRUCT_FILENAME_KEY="files"
'''
<relative file path>:<change type>:<revision> 
<relative file path> is a path to a file relative to the current checkout directory.
<change type> is a type of modification and can have the following values: CHANGED, ADDED, REMOVED, NOT_CHANGED, DIRECTORY_CHANGED, DIRECTORY_ADDED, DIRECTORY_REMOVED
<revision> is a file revision in repository. If file is a part of change list started via remote run then string <personal> will be written instead of file revision.
'''
def read_changed_info(sourceFile):
	changed_files = {}
	print("changed file " + sourceFile)
	#for line in sourceFile.split("\n"):
	for line in sourceFile.split('\n'):
		values = line.split(CHANGED_FILES_INFO_SEPARATOR)
		if values[0] and values[1]:
			changed_files[values[0]] = {CHANGE_TYPE_PROPERTY_NAME : values[1]}
	return changed_files

def send_emails(emailList):
	SMTPserver = 'purepower.atola.com'
	sender =     'noreply@atola.com'
	USERNAME = "robots@hdd-tools.com"
	PASSWORD = "CwyKKqW9XEoa"
	text_subtype = 'plain'
	subject="Your freshly made changes"
	
	
	conn = SMTP(SMTPserver)
	#conn.set_debuglevel(True) 
	try : 
		conn.login(USERNAME, PASSWORD)
		for email in emailList : 
			print("")
			print (str(email))
			content = 'Someone did some things to ' + ','.join(email[EMAIL_STRUCT_FILENAME_KEY]) + '\n. Please review.'
			print("content : " + content)
			msg = MIMEText(content, text_subtype)
			msg['Subject']= subject
			msg['From']   = sender
			destination = email[EMAIL_STRUCT_EMAIL_KEY]
			msg['To'] = email[EMAIL_STRUCT_EMAIL_KEY]
			conn.sendmail(sender, destination, msg.as_string())
	finally:
		conn.quit()
		


#read file with commited changes, format is specified here https://confluence.jetbrains.com/display/TCD7/Risk+Tests+Reordering+in+Custom+Test+Runner
file = open(CHANGED_FILES_PATH, 'r') 
changed_files = read_changed_info(file.read()) 

#email struct : {receiver : 'test@receiver.com', files : ['actual/file/name1.txt', 'actual/file/name2.txt']}
emails = []
with open(EMAIL_FILES_CONFIG_FILE, 'r') as configFile:
	config = json.load(configFile)
	for userConfig in config:
		print("userConfig " + str(userConfig))
		files = []
		for regexName in userConfig[JSON_FILE_PROP_NAME]:
			for fileName in changed_files.keys():
				if re.match(regexName, fileName):
					files.append(fileName)
					
		if files:
			emails.append({EMAIL_STRUCT_EMAIL_KEY : userConfig[JSON_EMAIL_PROP_NAME], EMAIL_STRUCT_FILENAME_KEY : files})

if emails:
	send_emails(emails)