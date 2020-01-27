#!/bin/env python

from configBot import *
import requests
import time, json
import watson_developer_cloud
creds = json.load(open("watson_creds.json"))
assistant = assistant = watson_developer_cloud.AssistantV1(username=watson_uid, password=watson_passwd, version="2018-02-16")


def WatsonCreateBot(botname):
	watsonBotId =  assistant.create_workspace(botname,description=botname, language=lang)["workspace_id"]
	print("WatsonBotId:",watsonBotId)
	return watsonBotId
	

def WatsonFindIntent(watsonBotId, utterance):
	return get_response(utterance)
	response = assistant.message(workspace_id=watsonBotId,input={"text": utterance},alternate_intents=False)

def get_response(text):
	url = creds["url"] 
	querystring = creds["querystring"] 
	payload =  creds["payload"] 
	payload["input"]["text"] = text
	payload["alternate_intents"] = creds.get("alternate_intents",False)
	headers =  creds["headers"]
	response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring).json()
	passed   = []
	scores   = []
	if len(response["intents"])>0:
		for intent in response["intents"]:
			if intent["confidence"]>=0:
				passed.append(intent["intent"])
				scores.append(str(intent["confidence"]))
			return [{"intent":"|".join(passed).replace("_"," ").lower(),"confidence":"|".join(scores)}]
		return response["intents"]
	else: return [{"intent":"None","confidence":-1}]

def WatsonCleanIntent(intent):
	cleanIntent = intent.replace(" ","").replace("\t","")
	if cleanIntent.lower() == "defaultfallbackintent":cleanIntent="None"
	return cleanIntent

def WatsonAddIntentAndUtterance(watsonBotId, intent,utterances):
	validIntent = WatsonCleanIntent(intent)
	assistant.create_intent(watsonBotId, validIntent, description=validIntent, examples=[{"text":utterance} for utterance in utterances])

