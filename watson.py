																																									#!/bin/env python

from configBot import *

import time, json
import watson_developer_cloud,requests

assistant = assistant = watson_developer_cloud.AssistantV1(iam_access_token="1_-cSfEyVs8J8MPbFIhcDSXqE_VQG2wJ7VyQaxfEyDYL",url="https://gateway-lon.watsonplatform.net/assistant/api", version="2018-08-01")


def WatsonCreateBot(botname):
	watsonBotId =  assistant.create_workspace(botname,description=botname, language=lang)["workspace_id"]
	print("WatsonBotId:",watsonBotId)
	return watsonBotId

def get_response(text):
	url = "https://assistant-eu-gb.watsonplatform.net/rest/v1/workspaces/899ca7d7-6391-4342-b051-4134f739b46a/message"

	querystring = {"version":"2018-07-10"}

	payload = {"input":{"text":text},"context":{"conversation_id":"ae46424c-3900-4119-80f8-0992e7023568","system":{"initialized":True,"dialog_stack":[{"dialog_node":"root"}],"dialog_turn_counter":2,"dialog_request_counter":2},"timezone":"Asia/Calcutta"},"alternate_intents":True}
	headers = {
    'Cookie': "JSESSIONID=s%3Ae9pBV_19VIOGfkOy0IkcwwCkgZGSYcsG.%2FA163B7I2PimMmeiOlB8hZg0bzRLVhzaO%2BW8K%2F02bz4; XSRF-TOKEN=SJXpg3Vm-1D0cK4sHyYtH0qDvUBjMc_og62k",
    'Origin': "https://assistant-eu-gb.watsonplatform.net",
    'X-XSRF-TOKEN': "SJXpg3Vm-1D0cK4sHyYtH0qDvUBjMc_og62k",
    'X-Watson-UserInfo': "bluemix-instance-id=65ae690a-2e43-46a5-8b77-663d97c4e0ca;bluemix-region-id=eu-gb;bluemix-crn=crn:v1:bluemix:public:conversation:eu-gb:a/0befbe5c22ed4b52b10f77ecd2ba8950:65ae690a-2e43-46a5-8b77-663d97c4e0ca::",
    'Accept-Language': "en-US,en;q=0.9,pt;q=0.8",
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Content-Type': "application/json;charset=UTF-8",
    'Accept': "application/json, text/plain, */*",
    'Referer': "https://assistant-eu-gb.watsonplatform.net/eu-gb/crn:v1:bluemix:public:conversation:eu-gb:a~2F0befbe5c22ed4b52b10f77ecd2ba8950:65ae690a-2e43-46a5-8b77-663d97c4e0ca::/workspaces/899ca7d7-6391-4342-b051-4134f739b46a/build/intents",
    'Accept-Encoding': "gzip, deflate, br",
    'Connection': "keep-alive",
    'DNT': "1",
    'cache-control': "no-cache",
    'Postman-Token': "ff923e92-cdb5-4a7e-a7cd-e3b4ab715733"
    }

	response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring).json()
	passed   = []
	scores   = []
	print(response)
	if len(response["intents"])>0:
		for intent in response["intents"]:
			if intent["confidence"]> 0.3:
				passed.append(intent["intent"])
				scores.append(str(intent["confidence"]))
		return [{"intent":"|".join(passed).replace("_"," ").lower(),"confidence":"|".join(scores)}]
	else: return [{"intent":"None","confidence":-1}]

def WatsonFindIntent(watsonBotId, utterance):
	resp = get_response(utterance)
	if "|" in resp[0]["intent"]:
		resp[0]["intent"] = "ambiguity:" +resp[0]["intent"] 
	return resp
	

def WatsonCleanIntent(intent):
	cleanIntent = intent.replace(" ","").replace("\t","")
	if cleanIntent.lower() == "defaultfallbackintent":cleanIntent="None"
	return cleanIntent

def WatsonAddIntentAndUtterance(watsonBotId, intent,utterances):
	validIntent = WatsonCleanIntent(intent)
	assistant.create_intent(watsonBotId, validIntent, description=validIntent, examples=[{"text":utterance} for utterance in utterances])

