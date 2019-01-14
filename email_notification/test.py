import json

with open('email_receivers.json', 'r') as configFile:
	config = json.load(configFile)
	print("whatever")
	print(str(config[0]))