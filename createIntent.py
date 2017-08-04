import requests, csv, os, time, sys, threading, getpass
from configBot import * #Calling the configuration file with all the static variables
from tqdm import tqdm
from google import *
from kore import *
from luis import *
reload(sys)
sys.setdefaultencoding('utf8')
#Global varibles used for reading input from the csv file
intents=[]
utterances=[]
loginResp=[]
urlL=[""]
input2={}
intentset=[]
idKore=[]
LuisIntentId=[]
def main():
#        botIDApi=""
#        Token_Api=""
        fr=open(fileName,'r')
        reader=csv.reader(fr,delimiter=',')
        for row in reader:
                if len(row)<=0:
                        continue
                if row[0]==None or row[0].strip()=='':
                        continue
                intents.append(row[1])
                utterances.append(row[2])
        fr.close()
        print("Finished reading training data.")

        if ssoKore is False:
                koreUserId=raw_input('Enter kore UserID: ')#login credentials for kore
                KorePassword=getpass.getpass('Enter kore Password: ')
                loginCred=loginToKore(koreUserId,KorePassword,KorePlatform)#Calling the login function for kore
                userIdKore=loginCred[1]                                         
                authTokenKore=loginCred[0]

        else:
                userIdKore=raw_input('Enter userid for kore: ')
                authTokenKore=raw_input('Enter authorization token for kore: ')
        headersKore['authorization']=authTokenKore #passing the authorization token to the configBot.py file
        botName=raw_input('Enter Bot Name: ')

        intentset.extend(list(set(intents)))
        botIDKore=createKoreBot(botName,userIdKore,authTokenKore,KorePlatform)#Bots creation for Luis and Kore
        print("New bot "+botName+" has been created in Kore with botid: "+ botIDKore)
        prepKore(intentset,intents,utterances,botIDKore,userIdKore,authTokenKore)

        if USELUIS:
            botIdLuis=createLuisBot(botName)
            print("New bot "+botName+" has been created in Luis with botid: " +botIdLuis)
            prepLuis(intentset,intents,utterances,botIdLuis)
        else:
            print("Not training LUIS")

        #For the google platform, we need to send all the training utterances for an intent at once.
        #Calling an empty dictionary to collect all these utterances.
        for i in range(len(intentset)):
            input2[intentset[i]]=[]

        for i in range(len(intents)):
            input2[intents[i]].append(utterances[i])

        if USEGOOGLE:
          print("Training Google bot after collecting all the train utterances")
          for j in tqdm(range(len(intentset))):
              addIntentAndUtteranceAPI(intentset[j],input2[intentset[j]])

        """
        for i in tqdm(range(len(intents))):
            if(intents[i]!=''):
                    if len(input2):
                 ###       addIntentAndUtteranceAPI(intentid,input2)#Calling googles function after collecting all the train utterances
                        while(len(input2)>0):input2.pop() 
             ###       LuisIntentId= addLuisIntent(intents[i],botIdLuis,subscriptionToken)#Adding Intent in Luis
             ###       idKore=addIntentKore(intents[i],botIDKore,userIdKore,authTokenKore,KorePlatform)#Adding Intent in Kore
                    print("New Intent "+intents[i]+" has been created")
                    intentid=intents[i]
                    addKoreUtterances(utterances[i],idKore[0],botIDKore,intentid,userIdKore,authTokenKore,KorePlatform)#Adding train utterances in Luis
                    addLuisUtterance(utterances[i],LuisIntentId,botIdLuis,intentid,subscriptionToken)#Adding train utterances in Kore
                    input2.append(utterances[i])#Adding training utterances for the google platform
            elif(intents[i]=='' or intents[i]==intentid):
                    input2.append(utterances[i])
                    addKoreUtterances(utterances[i],idKore[0],botIDKore,intentid,userIdKore,authTokenKore,KorePlatform)
                    addLuisUtterance(utterances[i],LuisIntentId,botIdLuis,intentid,subscriptionToken)
        addIntentAndUtteranceAPI(intentid,input2)#Calling function for the last Intent
        """
        print("Creating the config file for the read.py file.")
        createConfigFile(botName,botIDKore,userIdKore,authTokenKore,KorePlatform,urlL[0],botIDApi,Token_Api)

def prepLuis(intentset,intents,utterances,botIdLuis):
        print("Creating intents in luis")
        for i in tqdm(range(len(intentset))):
            LuisIntentId.append( addLuisIntent(intentset[i],botIdLuis))#Adding Intent in Luis

        print("Adding train utterances in Luis")
        th=[]
        for i in range(len(intents)):
            #addLuisUtterance(utterances[i],LuisIntentId[intentset.index(intents[i])],botIdLuis,intents[i])
            th.append(threading.Thread(target=addLuisUtterance,
                 args=([utterances[i],LuisIntentId[intentset.index(intents[i])],botIdLuis,intents[i]])))
            th[-1].start()
            
        for i in tqdm(range(len(intents))):
            th[i].join()
        print("Fetching the endpoint URL to hit, for Luis, to check response by its bot")           
        urlL.append(getLuisEndPointUrl(botIdLuis))


def prepKore(intentset, intents, utterances,botIDKore,userIdKore,authTokenKore):
        print("Creating intents in kore")
        for i in tqdm(range(len(intentset))):
            idKore.append(addIntentKore(intentset[i],botIDKore,userIdKore,authTokenKore,KorePlatform))

        th=[]
        print("Adding train utterances in Kore")
        for i in range(len(intents)):
            th.append(threading.Thread(target=addKoreUtterances,args=([utterances[i],idKore[intentset.index(intents[i])][0],botIDKore,intents[i],userIdKore,authTokenKore,KorePlatform])))
            th[i].start()
        for i in tqdm(range(len(intents))):
            #addKoreUtterances(utterances[i],idKore[intentset.index(intents[i])][0],botIDKore,intents[i],userIdKore,authTokenKore,KorePlatform)
            th[i].join()
        print("training the Kore bot")
        trainKore(botIDKore,userIdKore,authTokenKore,KorePlatform)


def createConfigFile(botName,botIDKore,userIdKore,authTokenKore,KorePlatform,urlL,botIDApi,Token_Api):
        fr=open('config.py','w')#Creating a config file for read, so as to be able to call read seperately
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
        fr.write("USEGOOGLE="+str(USEGOOGLE)+"\n")	
        fr.write("USELUIS="+str(USELUIS)+"\n")	

if __name__ == '__main__':
        main()
