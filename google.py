import requests
from configBot import *

def addIntentAndUtteranceAPI(APIIntent,APIUtterances):
        url = "https://console.api.ai/api/intents"
        string=''
        for i in range(len(APIUtterances)):
            string=string+"{\"isTemplate\":false,\"data\":[{\"text\":\""+APIUtterances[i]+"\"}],\"count\":0,\"id\":null,\"updated\":null}"+","
        string=string[0:-1]	
        payload = "{\"name\":\""+APIIntent+"\",\"auto\":true,\"contexts\":[],\"templates\":[],\"responses\":[{\"parameters\":[],\"resetContexts\":false,\"affectedContexts\":[],\"messages\":[],\"speech\":[],\"defaultResponsePlatforms\":{}}],\"source\":null,\"priority\":500000,\"cortanaCommand\":{\"navigateOrService\":\"NAVIGATE\",\"target\":\"\"},\"events\":[],\"userSays\":["+string+"]}"
        headers = {
    'authorization': "Bearer "+Token_Api,
    'content-type': "application/json;charset=UTF-8",
            }
        try:    
                response = requests.request("POST", url, data=payload, headers=headers)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

