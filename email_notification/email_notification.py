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

#format 		<relative file path>:<change type>:<revision> 
def read_changed_info(sourceFile):
	changed_files = {}
	print("changed file " + sourceFile)
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
	subject="Псс, немного изменений не хочешь?"
	
	conn = SMTP(SMTPserver)
	#conn.set_debuglevel(True) 
	try : 
		conn.login(USERNAME, PASSWORD)
		for email in emailList : 
			content = 'Посмотри, что наделали в ' + ', '.join(email[EMAIL_STRUCT_FILENAME_KEY]) + '. \nHave a good day.'
			msg = MIMEText(content, text_subtype)
			msg['Subject']= subject
			msg['From']   = sender
			msg['To'] = email[EMAIL_STRUCT_EMAIL_KEY]
			destination = email[EMAIL_STRUCT_EMAIL_KEY]
			print ("EMAIL : " + content)
			#conn.sendmail(sender, destination, msg.as_string())
	finally:
		conn.quit()
		
		
try : 
	#read file with commited changes, format is specified here https://confluence.jetbrains.com/display/TCD7/Risk+Tests+Reordering+in+Custom+Test+Runner
	file = open(CHANGED_FILES_PATH, 'r') 
	changed_files = read_changed_info(file.read()) 

	#email struct : {receiver : 'test@receiver.com', files : ['actual/file/name1.txt', 'actual/file/name2.txt']}
	emails = []
	with open(EMAIL_FILES_CONFIG_FILE, 'r') as configFile:
		config = json.load(configFile)
		for userConfig in config:
			files = []
			for regexName in userConfig[JSON_FILE_PROP_NAME]:
				for fileName in changed_files.keys():
					if re.match(regexName, fileName):
						files.append(fileName)
						
			if files:
				emails.append({EMAIL_STRUCT_EMAIL_KEY : userConfig[JSON_EMAIL_PROP_NAME], EMAIL_STRUCT_FILENAME_KEY : files})

	if emails:
		send_emails(emails)
except Exception as e: 
	print("Exception occured : " + str(e))