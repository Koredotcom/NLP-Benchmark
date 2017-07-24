import requests
from configBot import *
def loginToKore(koreUserId,KorePassword,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/oauth/token"
        payload = "{\"client_id\":\"1\",\"client_secret\":\"1\",\"scope\":\"1\",\"grant_type\":\"password\",\"username\":\""+koreUserId+"\",\"password\":\""+KorePassword+"\"}"
        headers = {'content-type': "application/json;charset=UTF-8"}
        try:
                response = requests.request("POST", url, data=payload, headers=headers)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        authTokenKore= "bearer "+response.json()['authorization']['accessToken']
        userIdKore=response.json()['authorization']['resourceOwnerID']
        loginResp=[authTokenKore, userIdKore]

        return loginResp

def createKoreBot(input,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/streams"
        payload = "{\"name\":\""+input+"\",\"type\":\"taskbot\",\"description\":\"faq\",\"color\":\"#1B3880\",\"categoryIds\":[\"451902a073c071463e2ce7c6\"],\"skipMakeEditLinks\":false,\"purpose\":\"customer\",\"errorCodes\":{\"pollError\":[]},\"visibility\":{\"namespace\":[],\"namespaceIds\":[]}}"
        try:
                response = requests.request("POST", url, data=payload, headers=headersKore)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        streamid=response.json()['_id']
        name=response.json()['name']

        url1 = "https://"+KorePlatform+"/api/1.1/market/streams"
        payload1 = "{\"_id\":\""+streamid+"\",\"name\":\""+name+"\",\"description\":\"faq\",\"categoryIds\":[\"451902a073c071463e2fe7f6\"],\"icon\":\"58d2376ab99576e94c2daf2c\",\"keywords\":[],\"languages\":[],\"price\":1,\"screenShots\":[],\"namespace\":\"private\",\"namespaceIds\":[],\"color\":\"#3AB961\",\"bBanner\":\"\",\"sBanner\":\"\",\"bBannerColor\":\"#3AB961\",\"sBannerColor\":\"#3AB961\",\"profileRequired\":true,\"sendVcf\":false}"
        try:
                response1 = requests.request("POST", url1, data=payload1, headers=headersKore)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        dgValue=callIntentKore('Default Fallback Intent',streamid,userIdKore,authTokenKore,KorePlatform)

        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"
        querystring = {"rnd":"7hl7dm"}
        try:
                response = requests.request("GET", url, headers=headersKore, params=querystring)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/defaultDialogSettings"
        querystring = {"rnd":"jw4tcv"}
        payload = "{\"defaultDialogId\":\""+dgValue[1]+"\"}"
        try:
                response = requests.request("POST", url, data=payload, headers=headersKore, params=querystring)             
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        return streamid
def callIntentKore(input,streamid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components"
        payload = "{\"desc\":\"\",\"type\":\"intent\",\"intent\":\""+input+"\"}"
        try:
                response = requests.request("POST", url, data=payload, headers=headersKore)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        name=response.json()['name']
        component=response.json()['_id']

        url2 = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"
        payload2 = "{\"name\":\""+name+"\",\"shortDesc\":\"News updates\",\"nodes\":[{\"nodeId\":\"intent0\",\"type\":\"intent\",\"componentId\":\""+component+"\",\"transitions\":[{\"default\":\"\",\"metadata\":{\"color\":\"#f3a261\",\"connId\":\"dummy0\"}}],\"metadata\":{\"left\":30,\"top\":170}}],\"visibility\":{\"namespace\":\"private\",\"namespaceIds\":[\"\"]}}"
        try:
                response2 = requests.request("POST", url2, data=payload2, headers=headersKore)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        name=response2.json()['name']
        dialogId=response2.json()['_id']

        url3 = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components/"+component+""
        payload3 = "{\"name\":\""+name+"\",\"dialogId\":\""+dialogId+"\"}"
        try:
                response3 = requests.request("PUT", url3, data=payload3, headers=headersKore)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        idKores=[component,dialogId]        
        return idKores
def callKoreUtterances(input,idKore,streamid,intentid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences"
        payload = "{\"taskId\":\""+idKore+"\",\"sentence\":\""+input+"\",\"streamId\":\""+streamid+"\",\"taskName\":\""+intentid+"\",\"type\":\"DialogIntent\"}"
        try:    
                response = requests.request("POST", url, data=payload, headers=headersKore)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)
def trainKore(streamid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences/ml/train"
        querystring = {"streamId":streamid,"rnd":"8ff5ai"}
        payload = "{}"
        headers = {'authorization': authTokenKore}
        try:
                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        except:
                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)

        return response
                                        
