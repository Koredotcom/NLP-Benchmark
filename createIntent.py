import requests, csv, os, time, sys, urllib,getpass
from configBot import *
import read
from tqdm import tqdm
reload(sys)
sys.setdefaultencoding('utf8')
intents=[]
utterances=[]
loginResp=[]
#input2=[]
def main():
        fr=open('Intent.csv','r')
        reader=csv.reader(fr,delimiter=',')
        #reader.next()
        if ssoKore is False:
                koreUserId=raw_input('Enter kore UserID: ')
                KorePassword=getpass.getpass('Enter kore Password: ')
                loginCred=loginToKore(koreUserId,KorePassword,KorePlatform)
        else:
                userIdKore=('Enter userid for kore: ')
                authTokenKore=('Enter authorization token for kore: ')	
        userIdKore=loginCred[1]
        authTokenKore=loginCred[0]
        botName=raw_input('Enter Bot Name: ')
        botIDKore=createKoreBot(botName,userIdKore,authTokenKore,KorePlatform)
        #botIDApi=createAPIbot(botName)
        botIdLuis=createLuisBot(botName,subscriptionToken)
        print("New bot "+botName+" has been created")
        #if botIdLuis.find('{')!=-1:
        #   raise Exception("Bot "+botName+" Not created")
        for row in reader:
                if len(row)<=0:
                        continue
                if row[0]==None or row[0].strip()=='':
                        continue
        
                intents.append(row[1])
                utterances.append(row[2])
        fr.close()
        input2=[]
        for i in tqdm(range(len(intents))):
            if(intents[i]!=''):
                    if len(input2):
                            addIntentAndUtteranceAPI(intentid,input2)
                            input2=[]
                    LuisIntentId= callLuisIntent(intents[i],botIdLuis,subscriptionToken)
                    idKore=callIntentKore(intents[i],botIDKore,userIdKore,authTokenKore,KorePlatform)
                    print("New Intent "+intents[i]+" has been created")
                    intentid=intents[i]
                    callKoreUtterances(utterances[i],idKore[0],botIDKore,intentid,userIdKore,authTokenKore,KorePlatform)
                    callLuisUtterance(utterances[i],LuisIntentId,botIdLuis,intentid,subscriptionToken)
                    input2.append(utterances[i])
            elif(intents[i]==''):
                    input2.append(utterances[i])
                    callKoreUtterances(utterances[i],idKore[0],botIDKore,intentid,userIdKore,authTokenKore,KorePlatform)
                    callLuisUtterance(utterances[i],LuisIntentId,botIdLuis,intentid,subscriptionToken)
        addIntentAndUtteranceAPI(intentid,input2)
        trainKore(botIDKore,userIdKore,authTokenKore,KorePlatform)
        urlL=getLuisEndPointUrl(botIdLuis,subscriptionToken)            
        createConfigFile(botName,botIDKore,userIdKore,authTokenKore,KorePlatform,urlL,botIDApi,Token_Api)

def loginToKore(koreUserId,KorePassword,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/oauth/token"

        payload = "{\"client_id\":\"1\",\"client_secret\":\"1\",\"scope\":\"1\",\"grant_type\":\"password\",\"username\":\""+koreUserId+"\",\"password\":\""+KorePassword+"\"}"
        headers = {
    'user-agent': "Mozilla/5.",
    'accept-language': "en-US,en;q=0.8",
    'content-type': "application/json;charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'cache-control': "no-cache",
    'postman-token': "550e6c64-828c-6049-d577-4140b7adc2db"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception        
        authTokenKore= "bearer "+response.json()['authorization']['accessToken']
        userIdKore=response.json()['authorization']['resourceOwnerID']
        loginResp=[authTokenKore, userIdKore]
        return loginResp
def trainKore(streamid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences/ml/train"

        querystring = {"streamId":streamid,"rnd":"8ff5ai"}

        payload = "{}"
        headers = {
    'authorization': authTokenKore,
    'origin': "https://"+KorePlatform,
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'content-type': "application/json;charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://"+KorePlatform+"/botbuilder",
    'cookie': "unq=AqKliyGHbty0bJRt; _ga=GA1.2.33823205.1499777365; _gid=GA1.2.378502692.1500097918",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "1ce810c2-6fe7-76e1-255a-1341d2f373e1"
            }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        #print(response.text)
        return response
        #flag=apiRequestErrors(response)
        #if(flag==1):
          #      raise Exception

def getLuisEndPointUrl(botIdLuis,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/assignedkey/"

        headers = {
    'access-control-request-method': "PUT",
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, sdch, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'accept': "*/*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/publish",
    'connection': "keep-alive",
    'access-control-request-headers': "content-type,ocp-apim-subscription-key",
    'cache-control': "no-cache",
    'postman-token': "1f387907-b0a4-e5e5-fa28-1563fd6d281c"
            }

        response = requests.request("OPTIONS", url, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/assignedkey/"

        payload = "\""+subscriptionToken+"\""
        headers = {
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, sdch, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'ocp-apim-subscription-key': subscriptionToken,
    'content-type': "application/json; charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/publish",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "5d8bce6b-a167-8734-f9ff-c0636ded9884"
            }

        response = requests.request("PUT", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"

        headers = {
    'access-control-request-method': "POST",
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, sdch, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'accept': "*/*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/publish",
    'connection': "keep-alive",
    'access-control-request-headers': "content-type,ocp-apim-subscription-key",
    'cache-control': "no-cache",
    'postman-token': "7eda6019-03a0-67fb-3917-b87ba7ea24df"
            }

        response = requests.request("OPTIONS", url, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"

        payload = "{}"
        headers = {
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'ocp-apim-subscription-key': subscriptionToken,
    'content-type': "application/json; charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/publish",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "9df6e2b7-f2d9-61a2-9704-223e131da770"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception        
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/train"

        headers = {
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, sdch, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'ocp-apim-subscription-key': subscriptionToken,
    'content-type': "application/json; charset=utf-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/publish",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "a265b278-eed2-0858-fa25-712cee9188b8"
            }

        response = requests.request("GET", url, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
          #      raise Exception

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/publish"

        payload = "{\"versionId\":\"0.1\",\"isStaging\":false}"
        headers = {
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'ocp-apim-subscription-key': subscriptionToken,
    'content-type': "application/json; charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/publish",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "e1cc6224-8a3b-4701-8928-8089f8ac43cf"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception        
        #print(response.text)
        endpointURL=response.json()['endpointUrl']+"?subscription-key="+response.json()['assignedEndpointKey']+"&timezoneOffset=0&verbose=true&q="
        return endpointURL
def createLuisBot(input,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"

        payload = str({"name":input,"description":"","culture":"en-us","domain":"","usageScenario":""})
        headers = {
                    'origin': "https://www.luis.ai",
                    'accept-encoding': "gzip, deflate, br",
                    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
                    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
                    'ocp-apim-subscription-key': subscriptionToken,
                    'content-type': "application/json; charset=UTF-8",
                    'accept': "application/json, text/plain, */*",
                    'referer': "https://www.luis.ai/applications",
                    'connection': "keep-alive",
                    'cache-control': "no-cache",
                    'postman-token': "008804fd-c105-de42-931d-424c371bb4be"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception
        return response.text.strip('"')

                    
def callLuisIntent(input,botIdLuis,subscriptionToken):

        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/intents"
 
        payload = str({"name":input})
        headers = {
            'origin': "https://www.luis.ai",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
            'ocp-apim-subscription-key': subscriptionToken,
            'content-type': "application/json; charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/intents",
            'connection': "keep-alive",
            'cache-control': "no-cache",
            'postman-token': "d4b08d0d-8acb-3620-b032-e93ef03d9633"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception        
        return response.text

def callLuisUtterance(input,LuisIntentId,botIdLuis,intentid,subscriptionToken):
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0//apps/"+botIdLuis+"/versions/0.1/examples"

        payload = "[{\"text\":\""+input+"\",\"intentName\":\""+intentid+"\",\"entityLabels\":[]}]"
        headers = {
    'origin': "https://www.luis.ai",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'ocp-apim-subscription-key': subscriptionToken,
    'content-type': "application/json; charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://www.luis.ai/application/"+botIdLuis+"/version/0.1/intents/"+LuisIntentId,
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "7b358eca-29ab-3891-c14e-02e2172bfc97"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception
def callAPIIntent(input,botIDApi):
        url2 = "https://console.api.ai/api/intents"

        payload = "{\"name\":"+input+",\"auto\":true,\"contexts\":[],\"templates\":[],\"responses\":[{\"parameters\":[],\"resetContexts\":false,\"affectedContexts\":[],\"messages\":[{\"type\":0,\"speech\":[]}],\"speech\":[],\"defaultResponsePlatforms\":{}}],\"source\":null,\"priority\":500000,\"cortanaCommand\":{\"navigateOrService\":\"NAVIGATE\",\"target\":\"\"},\"events\":[],\"userSays\":[]}"
        headers = {
            'origin': "https://console.api.ai",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
            'authorization': "Bearer "+botIDApi,
            'x-xsrf-token': "e915ee3a-926a-4f40-9ae4-8c61dc49963c",
            'content-type': "application/json;charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'authority': "console.api.ai",
            'cookie': "zUserAccessToken=11b5e202-599a-4d14-8960-7eff371455c9; _ga=GA1.2.950925124.1498229541; _gid=GA1.2.1131315499.1499618066; _gat=1",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
            'cache-control': "no-cache",
            'postman-token': "f506d2a1-53a8-0adf-b70e-66b48fe1b471"
            }

        response = requests.request("POST", url2, data=payload, headers=headers)
        flag=apiRequestErrors(response)
        if(flag==1):
                raise Exception        
        return response.status_code

def createAPIbot(input):
        url = "https://console.api.ai/api-client/agents"
        payload = "{\"name\":"+input+",\"description\":\"\",\"sampleData\":null,\"language\":\"en\",\"ownerId\":\"\",\"primaryKey\":\"\",\"secondaryKey\":\"\",\"enableFulfillment\":false,\"defaultTimezone\":\"Asia/Almaty\",\"googleAssistant\":{},\"isPrivate\":true,\"customClassifierMode\":\"use.after\",\"mlMinConfidence\":0.3,\"useCustomClassifier\":true,\"intentParamsAutoSync\":true}"
        headers = {
            'origin': "https://console.api.ai",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
            'x-xsrf-token': "c40a3e53-2390-4d5f-bc46-96f71ffcb6c4",
            'content-type': "application/json;charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'authority': "console.api.ai",
            'cookie': "JSESSIONID=3A9971B715E4A46BA2E40450C85FB23F; XSRF-TOKEN=c40a3e53-2390-4d5f-bc46-96f71ffcb6c4; currentUser=%22newbankbot%40gmail.com%22; zUserAccessToken=51eb81ca-205e-496c-898f-95c7c018898e; _ga=GA1.2.17316286.1500385408; _gid=GA1.2.1607925162.1500385408; _gat=1",
            'cache-control': "no-cache",
            'postman-token': "04c95277-ee87-d044-467c-c7fa70a90e7f"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception        
        return response.json()['id']

def createKoreBot(input,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/streams"
        payload = "{\"name\":\""+input+"\",\"type\":\"taskbot\",\"description\":\"faq\",\"color\":\"#1B3880\",\"categoryIds\":[\"451902a073c071463e2ce7c6\"],\"skipMakeEditLinks\":false,\"purpose\":\"customer\",\"errorCodes\":{\"pollError\":[]},\"visibility\":{\"namespace\":[],\"namespaceIds\":[]}}"
        headers = {
    'authorization': authTokenKore,
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "b155da17-c6da-e78b-3176-b3635f0d16e1"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception
        streamid=response.json()['_id']
        name=response.json()['name']
        url1 = "https://"+KorePlatform+"/api/1.1/market/streams"

        payload1 = "{\"_id\":\""+streamid+"\",\"name\":\""+name+"\",\"description\":\"faq\",\"categoryIds\":[\"451902a073c071463e2fe7f6\"],\"icon\":\"58d2376ab99576e94c2daf2c\",\"keywords\":[],\"languages\":[],\"price\":1,\"screenShots\":[],\"namespace\":\"private\",\"namespaceIds\":[],\"color\":\"#3AB961\",\"bBanner\":\"\",\"sBanner\":\"\",\"bBannerColor\":\"#3AB961\",\"sBannerColor\":\"#3AB961\",\"profileRequired\":true,\"sendVcf\":false}"
        headers1 = {
    'authorization': authTokenKore,
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "9e8d9609-3374-3d7d-0cf7-ed92701fff58"
            }

        response1 = requests.request("POST", url1, data=payload1, headers=headers1)
        #flag=apiRequestErrors(response)
        #if(flag==1):
            #    raise Exception   
        dgValue=callIntentKore('Default Fallback Intent',streamid,userIdKore,authTokenKore,KorePlatform)
        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"

        querystring = {"rnd":"7hl7dm"}

        headers = {
    'cookie': "unq=AqKliyGHbty0bJRt; _ga=GA1.2.33823205.1499777365; _gid=GA1.2.231463277.1500432635; connect.sid=s%3AbbxgXwfqf6PjmQOmoqWFg_gZJgk1kgTE.2%2B59J4ADokG3vipEdo6LPHIWokOljiSgVsV9FdWB7Eo",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'authorization': authTokenKore,
    'content-type': "application/json;charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://"+KorePlatform+"/botbuilder",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/59.0.3071.109 Chrome/59.0.3071.109 Safari/537.36",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "46825b1a-dda9-015a-79dc-f512c6a59a4e"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/defaultDialogSettings"

        querystring = {"rnd":"jw4tcv"}

        payload = "{\"defaultDialogId\":\""+dgValue[1]+"\"}"
        headers = {
    'authorization': authTokenKore,
    'origin': "https://"+KorePlatform,
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/59.0.3071.109 Chrome/59.0.3071.109 Safari/537.36",
    'content-type': "application/json;charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://"+KorePlatform+"/botbuilder",
    'cookie': "unq=AqKliyGHbty0bJRt; _ga=GA1.2.33823205.1499777365; _gid=GA1.2.231463277.1500432635; connect.sid=s%3AbbxgXwfqf6PjmQOmoqWFg_gZJgk1kgTE.2%2B59J4ADokG3vipEdo6LPHIWokOljiSgVsV9FdWB7Eo",
    'connection': "keep-alive",
    'x-http-method-override': "put",
    'cache-control': "no-cache",
    'postman-token': "48d0457e-1893-a288-17a1-77008b2acf8a"
            }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)             
        return streamid
def callIntentKore(input,streamid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components"

        payload = "{\"desc\":\"\",\"type\":\"intent\",\"intent\":\""+input+"\"}"
        headers = {
    'authorization': authTokenKore,
    'cache-control': "no-cache",
    'content-type': "application/json",
    'postman-token': "db326a7c-806f-6f18-9261-a1378b173a80"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception        
        name=response.json()['name']
        component=response.json()['_id']
        url2 = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/dialogs"

        payload2 = "{\"name\":\""+name+"\",\"shortDesc\":\"News updates\",\"nodes\":[{\"nodeId\":\"intent0\",\"type\":\"intent\",\"componentId\":\""+component+"\",\"transitions\":[{\"default\":\"\",\"metadata\":{\"color\":\"#f3a261\",\"connId\":\"dummy0\"}}],\"metadata\":{\"left\":30,\"top\":170}}],\"visibility\":{\"namespace\":\"private\",\"namespaceIds\":[\"\"]}}"
        headers2 = {
    'authorization': authTokenKore,
    'cache-control': "no-cache",
    'content-type': "application/json",
    'postman-token': "19284893-1fa7-d0c5-2289-8f0b7e6a8d8b"
            }

        response2 = requests.request("POST", url2, data=payload2, headers=headers2)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception        
        name=response2.json()['name']
        dialogId=response2.json()['_id']
        url3 = "https://"+KorePlatform+"/api/1.1/builder/streams/"+streamid+"/components/"+component+""

        payload3 = "{\"name\":\""+name+"\",\"dialogId\":\""+dialogId+"\"}"
        headers3 = {
    'authorization': authTokenKore,
    'cache-control': "no-cache",
    'content-type': "application/json",
    'postman-token': "9e3b6068-cb5f-dd01-0661-e3909e84a0cc"
            }

        response3 = requests.request("PUT", url3, data=payload3, headers=headers3)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception
        idKores=[component,dialogId]        
        return idKores

def callKoreUtterances(input,idKore,streamid,intentid,userIdKore,authTokenKore,KorePlatform):
        url = "https://"+KorePlatform+"/api/1.1/users/"+userIdKore+"/builder/sentences"

        payload = "{\"taskId\":\""+idKore+"\",\"sentence\":\""+input+"\",\"streamId\":\""+streamid+"\",\"taskName\":\""+intentid+"\",\"type\":\"DialogIntent\"}"
        headers = {
    'authorization': authTokenKore,
    'origin': "https://"+KorePlatform,
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'content-type': "application/json;charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'referer': "https://"+KorePlatform+"/botbuilder",
    'cookie': "unq=AqKliyGHbty0bJRt; _ga=GA1.2.33823205.1499777365; _gid=GA1.2.2066209900.1499777365",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'postman-token': "0b115645-afda-67cf-d626-be500bbe58ae"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
         #       raise Exception
def createConfigFile(botName,botIDKore,userIdKore,authTokenKore,KorePlatform,urlL,botIDApi,Token_Api):
        fr=open('config.py','w')
        fr.write("botname_QAbots=\""+botName+"\"\n")
        fr.write("uid_QAbots=\""+userIdKore+"\"\n")
        fr.write("token_QAbots=\""+authTokenKore+"\"\n")
        fr.write("streamid_QAbots=\""+botIDKore+"\"\n")
        fr.write("urlKa=\"https://"+KorePlatform+"/api/1.1/users/\"\n")
        fr.write("urlKb=\"/builder/streams/\"\n")
        fr.write("urlKc=\"/findIntend\"\n")
        fr.write("FileName=\"ML_TestData.csv\"\n")
        fr.write("Token_Api=\""+Token_Api+"\"\n")
        fr.write("url=\"https://console.api.ai/api/query\"\n")
        fr.write("botname_API=\""+botIDApi+"\"\n")
        fr.write("urlL=\""+urlL+"\"\n")	

def addIntentAndUtteranceAPI(input1,input2):
        url = "https://console.api.ai/api/intents"
        for i in range(len(input1)):
                if i is 0:
                        str="{\"isTemplate\":false,\"data\":[{\"text\":\""+input2[i]+"\"}],\"count\":0,\"id\":null,\"updated\":null}"
                str=str+","+"{\"isTemplate\":false,\"data\":[{\"text\":\""+input2[i]+"\"}],\"count\":0,\"id\":null,\"updated\":null}"	
        payload = "{\"name\":\""+input1+"\",\"auto\":true,\"contexts\":[],\"templates\":[],\"responses\":[{\"parameters\":[],\"resetContexts\":false,\"affectedContexts\":[],\"messages\":[],\"speech\":[],\"defaultResponsePlatforms\":{}}],\"source\":null,\"priority\":500000,\"cortanaCommand\":{\"navigateOrService\":\"NAVIGATE\",\"target\":\"\"},\"events\":[],\"userSays\":["+str+"]}"
        headers = {
    'origin': "https://console.api.ai",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.8,en;q=0.6",
    'authorization': "Bearer "+Token_Api,
    'x-xsrf-token': "c40a3e53-2390-4d5f-bc46-96f71ffcb6c4",
    'content-type': "application/json;charset=UTF-8",
    'accept': "application/json, text/plain, */*",
    'authority': "console.api.ai",
    #'cookie': cookieAPI,
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    'cache-control': "no-cache",
    'postman-token': "cd71a45f-e466-7209-3778-f4621f7196de"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        #flag=apiRequestErrors(response)
        #if(flag==1):
                #raise Exception
def apiRequestErrors(response):
        if(response.status_code != 200 or response.status_code != 201):
                print(response.text)
                return 1
        return 0        
if __name__ == '__main__':
        main()
        print("Waiting for the bots to train")
        time.sleep(45)
        read.main()
