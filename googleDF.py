import requests
from configBot import *

def addIntentAndUtteranceDF(DFIntent,DFUtterances):
        url = "https://console.dialogflow.com/api/intents"
        string=[{"isTemplate":False,"data":[{"text":DFUtterances[i]}],"count":0,"id":None,"updated":None}
                                             for i in range(len(DFUtterances))]

        #Training utterances have to be sent in the above format. Hence saved for all trian utterances in a string and passed it on the payload.
        payload = {"name":DFIntent,"auto":True,"contexts":[],"templates":[],"responses":[{"parameters":[],"resetContexts":False,"affectedContexts":[],"messages":[],"speech":[],"defaultResponsePlatforms":{}}],"source":None,"priority":500000,"cortanaCommand":{"navigateOrService":"NAVIGATE","target":""},"events":[],"userSays":string}
        headers = {
    'authorization': "Bearer "+Token_DF,#Fetched from config file.
    'content-type': "application/json;charset=UTF-8",
            }
        try:    
                response = requests.post( url, json=payload, headers=headers)
        except:
                raise Exception("Error while adding intent and utterances for google")


def getIntentsInBot():
	url = "https://console.dialogflow.com/api/intents"

	headers = {
    'authorization': "Bearer "+botIdDF,
    'cookie': "zUserAccessToken=55222461-14c3-4d71-ad86-39df2d2b6a81"
    }

	response = requests.get( url, headers=headers)
	print(response.text)
