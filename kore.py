import requests, time, json
from configBot import *
headersKore = {"content-type": "application/json;charset=UTF-8"}

def loginToKore(koreUserId,KorePassword,KorePlatform):
        url = KorePlatform+"/api/1.1/oauth/token"#Calling the oauth Api for Kore
        payload = "{\"client_id\":\"1\",\"client_secret\":\"1\",\"scope\":\"1\",\"grant_type\":\"password\",\"username\":\""+koreUserId+"\",\"password\":\""+KorePassword+"\"}"
        headers = {'content-type': "application/json;charset=UTF-8"}
        try:
                response = requests.post(url, data=payload, headers=headers)
        except:
                print(response.text)

        authTokenKore= "bearer "+response.json()['authorization']['accessToken']
        userIdKore=response.json()['authorization']['resourceOwnerID']
        loginResp=[authTokenKore, userIdKore]

        return loginResp

def builderStreams1(Input, userIdKore, authTokenKore, KorePlatform):
        url = KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/streams"#Calling the builder Api for Kore
        payload = "{\"name\":\""+Input+"\",\"type\":\"taskbot\",\"description\":\"drfgd\",\"color\":\"#FF7A00\",\"categoryIds\":[\"451902a073c071463e2fe7f6\"],\"skipMakeEditLinks\":false,\"purpose\":\"customer\",\"errorCodes\":{\"pollError\":[]},\"visibility\":{\"namespace\":[],\"namespaceIds\":[]},\"defaultLanguage\":\"en\"}"
        try:
                response = requests.post(url, data=payload, headers=headersKore)
                streamid=response.json()['_id']
                name=response.json()['name']
                #print("builder streams 1", response.text)
        except:
                raise Exception("Error while creating builder streams")        
        return name,streamid

def builderStreams1_5(Input, userIdKore, authTokenKore, KorePlatform):
        url = "http://localhost/api/1.1/users/"++"/builder/streams"
        querystring = {"rnd":"9in6m"}
        response = requests.get( url, headers=headers, params=querystring)
        print(response.text)

def marketStreams1(Input, userIdKore, authTokenKore, KorePlatform, name, streamid):
        url1 = KorePlatform+"/api/1.1/market/streams"#Calling the Market streams Api
        if KorePlatform.split("//")[1].split(".")[0] == "pilot-bots": 
            icon = "59c0f641da89738e6f467d82"
        else:
            icon = "58d2376ab99576e94c2daf2c"
        payload1 = "{\"_id\":\""+streamid+"\",\"name\":\""+name+"\",\"description\":\"faq\",\"categoryIds\":[\"451902a073c071463e2fe7f6\"],\"icon\":\""+icon+"\",\"keywords\":[],\"languages\":[],\"price\":1,\"screenShots\":[],\"namespace\":\"private\",\"namespaceIds\":[],\"color\":\"#3AB961\",\"bBanner\":\"\",\"sBanner\":\"\",\"bBannerColor\":\"#3AB961\",\"sBannerColor\":\"#3AB961\",\"profileRequired\":true,\"sendVcf\":false}"
        try:
                response1 = requests.post(url1, data=payload1, headers=headersKore)
                response1.raise_for_status()
                #print("market streams 1",response1.text)
        except Exception as e:
                raise Exception("Error while creating Market streams"+str(e))
        return addIntentKore('Default Fallback Intent',streamid,userIdKore,authTokenKore,KorePlatform)

def builderStreams2(Input, userIdKore, authTokenKore, KorePlatform, streamid):
        url = KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"
        querystring = {"rnd":"7hl7dm"}
        try:
                response = requests.get(url, headers=headersKore, params=querystring)
                response.raise_for_status()
                #print("builderstreams 2",response.text)
        except:
                raise Exception("Error while creating Setting Default dialog task streams")

def builderStreams3(Input, userIdKore, authTokenKore, KorePlatform, streamid, dgValue):
        url = KorePlatform+"/api/1.1/builder/streams/"+streamid+"/defaultDialogSettings"
        #Setting the Default Dialog Task to Default Fallback Intent. 
        querystring = {"rnd":"jw4tcv"}
        payload = "{\"defaultDialogId\":\""+dgValue[1]+"\"}"
        headers = {}
        headers['content-type'] = headersKore['content-type']
        headers['authorization'] = authTokenKore
        headers['x-http-method-override'] = 'put'
        try:
                response = requests.post(url, data=payload, headers=headers, params=querystring)             
                response.raise_for_status()
                print("RESP post",response)
        except:
                raise Exception("Error while creating Setting Default dialog task streams")        

def getAccountId(userIdKore, authTokenKore, KorePlatform):

    url = KorePlatform+"/api/1.1/users/"+userIdKore+"/AppControlList"
    headers = {
    'authorization': authTokenKore,
    'bot-language': "en",
    'content-type': "application/json",
    }
    response = requests.get( url, headers=headers)
    response = json.loads(response.text)
    #print(response.text)
    ret =  response["associatedAccounts"][0]["accountId"]
    print(ret)
    return ret

def createKoreBot(Input, userIdKore, authTokenKore, KorePlatform):
        headersKore['host']= "localhost"
        headersKore['user-agent']= "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
        headersKore['accept']= "application/json, text/plain, */*"
        headersKore['accept-language']= "en-US,en;q=0.5"
        headersKore['referer']= "http://localhost/botbuilder"
        headersKore['authorization']= authTokenKore
        headersKore['bot-language']= "en"
        headersKore['accountid']= getAccountId(userIdKore,authTokenKore,KorePlatform)
        name, streamid = builderStreams1(Input, userIdKore, authTokenKore, KorePlatform)

        dgValue = marketStreams1(Input, userIdKore, authTokenKore, KorePlatform, name, streamid)

        builderStreams2(Input, userIdKore, authTokenKore, KorePlatform, streamid)
        builderStreams3(Input, userIdKore, authTokenKore, KorePlatform, streamid, dgValue)


        return streamid

def addIntentKore(Input,streamid,userIdKore,authTokenKore,KorePlatform):
        url = KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components"
        payload = json.dumps({"desc":"","type":"intent","intent":Input})
        try:
                response = requests.post( url+"?rnd=h3uyn", data=payload, headers=headersKore)
                response.raise_for_status()
        except:
                print(response.text)
                raise Exception("Error while Adding intent to kore 1")

        name=response.json()['name']
        component=response.json()['_id']

        url2 = KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"
        payload2 = "{\"name\":\""+name+"\",\"shortDesc\":\"News updates\",\"nodes\":[{\"nodeId\":\"intent0\",\"type\":\"intent\",\"componentId\":\""+component+"\",\"transitions\":[{\"default\":\"\",\"metadata\":{\"color\":\"#f3a261\",\"connId\":\"dummy0\"}}],\"metadata\":{\"left\":30,\"top\":170}}],\"visibility\":{\"namespace\":\"private\",\"namespaceIds\":[\"\"]}}"
        try:
                response2 = requests.post( url2, data=payload2, headers=headersKore)
        except:
                raise Exception("Error while Adding intent to kore 2")

        name=response2.json()['name']
        dialogId=response2.json()['_id']

        url3 = KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components/"+component+""
        payload3 = "{\"name\":\""+name+"\",\"dialogId\":\""+dialogId+"\"}"
        try:
                response3 = requests.put(url3, data=payload3, headers=headersKore)
        except:
                raise Exception("Error while Adding intent to kore 3")

        idKores=[component,dialogId]
        return idKores

def addKoreUtterances(Input, idKore, streamid, intentid, userIdKore, authTokenKore, KorePlatform):
        url = KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences"
        #payload = "{\"taskId\":\""+idKore+"\",\"sentence\":\""+Input+"\",\"streamId\":\""+streamid+"\",\"taskName\":\""+intentid+"\",\"type\":\"DialogIntent\"}"
        payload = json.dumps({"taskId":idKore,"sentence":Input,"streamId":streamid,"taskName":intentid,"type":"DialogIntent"})
        while 1:
            try:
                response = requests.post( url, data=payload, headers=headersKore)
                if response.status_code==409: break
                response.raise_for_status()
            except:
                print("Error while adding training Utterances")
                if not 'response' in locals(): response={}
                else: print("addKoreUtterances", Input, idKore, streamid, intentid, userIdKore, authTokenKore, KorePlatform, response.status_code, response.text)

def trainKore(streamid,userIdKore,authTokenKore,KorePlatform):
        url = KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences/ml/train"
        querystring = {"streamId":streamid,"rnd":"8ff5ai"}
        payload = "{}"
        headers = {'authorization': authTokenKore}
        try:
                response = requests.post(url, data=payload, headers=headers, params=querystring)
        except:
                raise Exception("Error while training Utterances")        

        return response

