import requests
from configBot import *

def loginToKore(koreUserId,KorePassword,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/oauth/token"#Calling the oauth Api for Kore
        payload = "{\"client_id\":\"1\",\"client_secret\":\"1\",\"scope\":\"1\",\"grant_type\":\"password\",\"username\":\""+koreUserId+"\",\"password\":\""+KorePassword+"\"}"
        headers = {'content-type': "application/json;charset=UTF-8"}
        try:
                response = requests.request("POST", url, data=payload, headers=headers)
        except:
                print(response.text)

        authTokenKore= "bearer "+response.json()['authorization']['accessToken']
        userIdKore=response.json()['authorization']['resourceOwnerID']
        loginResp=[authTokenKore, userIdKore]

        return loginResp

def createKoreBot(input,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/streams"#Calling the builder Api for Kore
        payload = "{\"name\":\""+input+"\",\"type\":\"taskbot\",\"description\":\"faq\",\"color\":\"#1B3880\",\"categoryIds\":[\"451902a073c071463e2ce7c6\"],\"skipMakeEditLinks\":false,\"purpose\":\"customer\",\"errorCodes\":{\"pollError\":[]},\"visibility\":{\"namespace\":[],\"namespaceIds\":[]}}"
        try:
                response = requests.request("POST", url, data=payload, headers=headersKore)
                streamid=response.json()['_id']
                name=response.json()['name']
        except:
                raise Exception("Error while creating builder streams")        

        url1 = "https://"+KorePlatform+"/api/1.1/market/streams"#Calling the Market streams Api
        payload1 = "{\"_id\":\""+streamid+"\",\"name\":\""+name+"\",\"description\":\"faq\",\"categoryIds\":[\"451902a073c071463e2fe7f6\"],\"icon\":\"58d2376ab99576e94c2daf2c\",\"keywords\":[],\"languages\":[],\"price\":1,\"screenShots\":[],\"namespace\":\"private\",\"namespaceIds\":[],\"color\":\"#3AB961\",\"bBanner\":\"\",\"sBanner\":\"\",\"bBannerColor\":\"#3AB961\",\"sBannerColor\":\"#3AB961\",\"profileRequired\":true,\"sendVcf\":false}"
        try:
                response1 = requests.request("POST", url1, data=payload1, headers=headersKore)
                dgValue=addIntentKore('Default Fallback Intent',streamid,userIdKore,authTokenKore,KorePlatform)#Creating the default fallback intent and fetching a value necessary for further task.
        except:
                raise Exception("Error while creating Market streams")        


        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"
        querystring = {"rnd":"7hl7dm"}
        try:
                response = requests.request("GET", url, headers=headersKore, params=querystring)
        except:
                raise Exception("Error while creating Setting Default dialog task streams")        

        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/defaultDialogSettings"#Setting the Default Dialog Task to Default Fallback Intent. 
        querystring = {"rnd":"jw4tcv"}
        payload = "{\"defaultDialogId\":\""+dgValue[1]+"\"}"
        try:
                response = requests.request("POST", url, data=payload, headers=headersKore, params=querystring)             
        except:
                raise Exception("Error while creating Setting Default dialog task streams")        

        return streamid

def addIntentKore(input,streamid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components"
        payload = "{\"desc\":\"\",\"type\":\"intent\",\"intent\":\""+input+"\"}"
        try:
                response = requests.request("POST", url, data=payload, headers=headersKore)
        except:
                raise Exception("Error while Adding intent to kore")        

        name=response.json()['name']
        component=response.json()['_id']

        url2 = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"
        payload2 = "{\"name\":\""+name+"\",\"shortDesc\":\"News updates\",\"nodes\":[{\"nodeId\":\"intent0\",\"type\":\"intent\",\"componentId\":\""+component+"\",\"transitions\":[{\"default\":\"\",\"metadata\":{\"color\":\"#f3a261\",\"connId\":\"dummy0\"}}],\"metadata\":{\"left\":30,\"top\":170}}],\"visibility\":{\"namespace\":\"private\",\"namespaceIds\":[\"\"]}}"
        try:
                response2 = requests.request("POST", url2, data=payload2, headers=headersKore)
        except:
                raise Exception("Error while Adding intent to kore")        

        name=response2.json()['name']
        dialogId=response2.json()['_id']

        url3 = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components/"+component+""
        payload3 = "{\"name\":\""+name+"\",\"dialogId\":\""+dialogId+"\"}"
        try:
                response3 = requests.request("PUT", url3, data=payload3, headers=headersKore)
        except:
                raise Exception("Error while Adding intent to kore")        

        idKores=[component,dialogId]        
        return idKores

def addKoreUtterances(input,idKore,streamid,intentid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences"
        payload = "{\"taskId\":\""+idKore+"\",\"sentence\":\""+input+"\",\"streamId\":\""+streamid+"\",\"taskName\":\""+intentid+"\",\"type\":\"DialogIntent\"}"
        try:    
                response = requests.request("POST", url, data=payload, headers=headersKore)
        except:
                raise Exception("Error while adding training Utterances")        

def trainKore(streamid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences/ml/train"
        querystring = {"streamId":streamid,"rnd":"8ff5ai"}
        payload = "{}"
        headers = {'authorization': authTokenKore}
        try:
                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        except:
                raise Exception("Error while training Utterances")        

        return response
                                        
