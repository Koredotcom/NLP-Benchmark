import requests,time
from configBot import *

def createLuisBot(input,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"
        payload = str({"name":input,"description":"","culture":"en-us","domain":"","usageScenario":""})
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                raise Exception("Error while creating a bot in Luis")        

        return response.text.strip('"')            

def addLuisIntent(input,botIdLuis,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/intents"
        payload = str({"name":input})
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                raise Exception("Error while creating an Intent in Luis")        

        return response.text

def addLuisUtterance(input,LuisIntentId,botIdLuis,intentid,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/examples"
        payload = "[{\"text\":\""+input+"\",\"intentName\":\""+intentid+"\",\"entityLabels\":[]}]"
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                raise Exception("Error while adding trianing utterances in Luis")        

def getLuisEndPointUrl(botIdLuis,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/assignedkey/"
        headers = {
            'access-control-request-method': "PUT",
            'origin': "https://www.luis.ai",
            }
        try:    
                response = requests.request("OPTIONS", url, headers=headers)
        except:
                raise Exception("Error while trianing utterances in Luis")        

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/assignedkey/"
        payload = "\""+subscriptionToken+"\""
        try:
                response = requests.request("PUT", url, data=payload, headers=headerLuis)
        except:
                raise Exception("Error while trianing utterances in Luis")        

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"
        headers = {
            'access-control-request-method': "POST",
            'origin': "https://www.luis.ai",
            }
        payload = "{}"
        try:
                response = requests.request("OPTIONS", url, headers=headers)
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                raise Exception("Error while trianing utterances in Luis")        

        while(1):
            try:
                response = requests.request("OPTIONS", url, headers=headers)
                response = requests.request("GET", url, headers=headerLuis)
#                if response.json()[0]['details']['status'] !='UpToDate':
#                    print(response.json()[0]['details']['status'])
#                    raise Exception("NOT UPTODATE")
                break
            except:
                print("Error while checking training status in Luis")
                time.sleep(5)
        
        print("Waiting for bots to train") 
#        time.sleep(60) #Leaving 1 minute time for training the Luis bot

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/publish"
        payload = "{\"versionId\":\"0.1\",\"isStaging\":false}"
        while(1):
            try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
            except:
                raise Exception("Error while publishing app in Luis")        

            try:
                endpointURL=response.json()['endpointUrl']+"?subscription-key="+response.json()['assignedEndpointKey']+"&timezoneOffset=0&verbose=true&q="
                return endpointURL
            except:
                print("Could not fetch the endpoint in Luis:: trying to get end point after 5 seconds")
                time.sleep(5)
