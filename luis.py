import requests,time
from configBot import *

def createLuisBot(input,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"
        payload = str({"name":input,"description":"","culture":"en-us","domain":"","usageScenario":""})
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        return response.text.strip('"')            

def callLuisIntent(input,botIdLuis,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/intents"
        payload = str({"name":input})
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        return response.text

def callLuisUtterance(input,LuisIntentId,botIdLuis,intentid,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/examples"
        payload = "[{\"text\":\""+input+"\",\"intentName\":\""+intentid+"\",\"entityLabels\":[]}]"
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)
def getLuisEndPointUrl(botIdLuis,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/assignedkey/"
        headers = {
            'access-control-request-method': "PUT",
            'origin': "https://www.luis.ai",
            }
        try:    
                response = requests.request("OPTIONS", url, headers=headers)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/assignedkey/"
        payload = "\""+subscriptionToken+"\""
        try:
                response = requests.request("PUT", url, data=payload, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"
        headers = {
            'access-control-request-method': "POST",
            'origin': "https://www.luis.ai",
            }
        try:
                response = requests.request("OPTIONS", url, headers=headers)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"
        payload = "{}"
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"
        try:
                response = requests.request("GET", url, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        time.sleep(60)

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/publish"
        payload = "{\"versionId\":\"0.1\",\"isStaging\":false}"
        try:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
        except:
                response = requests.request("POST", url, data=payload, headers=headerLuis)
                print(response.text)

        endpointURL=response.json()['endpointUrl']+"?subscription-key="+response.json()['assignedEndpointKey']+"&timezoneOffset=0&verbose=true&q="
        return endpointURL

