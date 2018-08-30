'''

Author: @Ranjith Reddy;;; Created On 24/07/2018

'''

import json,os,sys,subprocess
from datetime import datetime
from translate import googleTranslate
from tqdm import tqdm

langmaps={
	 "en":"en",
	 "de":"de",
	 "fr":"fr",
	 "es":"es",
	 "zh_cn":"zh-cn",
	 "zh_tw":"zh-tw",
	 "pt":"pt",
	 "it":"it",
	 "ar":"ar",
	 "ja":"ja",
	 "ko":"ko",
	 "id":"id",
	 "nl":"nl",
	 "hi":"hi"
}

def langValidation(v):
	if v:
		v=v.lower()
		if v not in langmaps:
			print("Enter language is not supported")
			return True
	else:
		return True
	return False

def validateOption(option):
	allOptions="abcdefgh"
	if option in allOptions:
		return False
	return True

def user_display():
	print("Select an option to Translate: ")
	print("a) BotDefinition")
	print("b) MlSentences")
	print("c) FAQS")
	print("d) Automation Suite")
	print("e) BatchTest Suite")
	print("f) Template Locales")
	print("g) koraGenericResponses")
	print("h) defaultErrorCodeScript")

def read_input():
	loop=True
	data=[]
	while loop:
		user_display()
		option = input()
		if option:
			loop=validateOption(option.lower())
		else:
			print("Sorry we cannot proceed!! Please select from the given option")

	data.append(option.lower())
	loop=True
	while loop:
		print("Please enter SRC Language: ")
		src=input()
		loop=langValidation(src)

	data.append(src.lower())
	loop=True
	while loop:
		print("Please enter Destination Language:")
		dest=input()
		loop=langValidation(dest)
	data.append(dest.lower())

	print("Enter file path:")
	filepath=input()
	path=filepath
	data.append(path)
	return data

def Process():
	inp = read_input()
	option=inp[0].lower()
	src=inp[1].lower()
	dest=inp[2].lower()
	path=inp[3]
	with open(path,"r") as f:
		payload=json.load(f)
	gTrans = googleTranslate(langmaps[src],langmaps[dest])
	if option == 'a':
		gTrans.BotDefinition(payload,dest,src)
	elif option == 'b':
		gTrans.MlSentences(payload)
	elif option == 'c':
		gTrans.FAQS(payload)
	elif option == 'd':
		gTrans.AutomationSuite(payload)
	elif option == 'e':
		gTrans.BatchTestSuite(payload)
	elif option == 'f':
		gTrans.localeCodes(payload)
	elif option == 'g':
		gTrans.koraGenericResponses(payload)
	elif option == 'h':
		gTrans.defaultErrorCodeScript(payload)
	jsonstring = json.dumps(payload).replace('"'+src+'"','"'+dest+'"')
	payload    = json.loads(jsonstring)
	translatedFile = str(datetime.now()).split('.')[0].replace(" ","_") 
	with open(translatedFile+".json", 'w', encoding='utf-8') as f:
		json.dump(payload,f,ensure_ascii=False,indent=4)

if __name__ == '__main__':
	Process()