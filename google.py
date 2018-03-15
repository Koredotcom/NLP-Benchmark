import requests
from configBot import *

def addIntentAndUtteranceDF(DFIntent,DFUtterances):
        url = "https://console.dialogflow.com/api/intents"
        string=''
        for i in range(len(DFUtterances)):
            string=string+"{\"isTemplate\":false,\"data\":[{\"text\":\""+DFUtterances[i]+"\"}],\"count\":0,\"id\":null,\"updated\":null}"+","
        string=string[0:-1]	#Training utterances have to be sent in the above format. Hence saved for all trian utterances in a string and passed it on the payload.
        payload = "{\"name\":\""+DFIntent+"\",\"auto\":true,\"contexts\":[],\"templates\":[],\"responses\":[{\"parameters\":[],\"resetContexts\":false,\"affectedContexts\":[],\"messages\":[],\"speech\":[],\"defaultResponsePlatforms\":{}}],\"source\":null,\"priority\":500000,\"cortanaCommand\":{\"navigateOrService\":\"NAVIGATE\",\"target\":\"\"},\"events\":[],\"userSays\":["+string+"]}"
        headers = {
    'authorization': "Bearer "+Token_DF,#Fetched from config file.
    'content-type': "application/json;charset=UTF-8",
            }
        try:    
                response = requests.request("POST", url, data=payload, headers=headers)
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
