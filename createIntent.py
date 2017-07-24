import requests, csv, os, time, sys, urllib,getpass
from configBot import *
from tqdm import tqdm
from google import *
from kore import *
from luis import *
reload(sys)
sys.setdefaultencoding('utf8')
intents=[]
utterances=[]
loginResp=[]
def main():
        fr=open(fileName,'r')
        reader=csv.reader(fr,delimiter=',')
        if ssoKore is False:
                koreUserId=raw_input('Enter kore UserID: ')
                KorePassword=getpass.getpass('Enter kore Password: ')
                loginCred=loginToKore(koreUserId,KorePassword,KorePlatform)
                userIdKore=loginCred[1]                                         
                authTokenKore=loginCred[0]

        else:
                userIdKore=raw_input('Enter userid for kore: ')
                authTokenKore=raw_input('Enter authorization token for kore: ')
        headersKore['authorization']=authTokenKore  	
        botName=raw_input('Enter Bot Name: ')
        botIDKore=createKoreBot(botName,userIdKore,authTokenKore,KorePlatform)
        botIdLuis=createLuisBot(botName,subscriptionToken)
        print("New bot "+botName+" has been created")
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
                            while(len(input2)>0):input2.pop() 
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
        keysToRead={"botname_QAbots":botName,"uid_QAbots":userIdKore,"token_QAbots":authTokenKore,"streamid_QAbots":botIDKore,"urlKa":"https://"+KorePlatform+"/api/1.1/users/","urlKb":"/builder/streams/","urlKc":"/findIntends","FileName":"ML_TestData.csv","Token_Api":Token_Api,"url":"https://console.api.ai/api/query","botname_API":botIDApi,"urlL":urlL}
        return keysToRead

if __name__ == '__main__':
        main()
