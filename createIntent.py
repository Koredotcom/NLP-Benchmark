import requests, csv, os, time, sys, threading, getpass, json
from six.moves import input
from configBot import *
from tqdm import tqdm
from google import *
from kore import *
from luis import *
#reload(sys)
#sys.setdefaultencoding('utf8')
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
        fr=open(fileName,'r')
        reader=csv.reader(fr,delimiter=',')
        for row in reader:
                if len(row)<=0:
                        continue
                row[0] =row[0].strip().lower().replace("-","")
                if row[0]==None or row[0].strip()=='':
                        continue
                while '  ' in row[0]: row[0] =row[0].replace('  ',' ')
                if not row[1] in utterances:
                        intents.append(row[0])
                        utterances.append(row[1])
        fr.close()
        intentset.extend(list(set(intents)))
        print(len(intentset), len(utterances),"distinct intents, distinct utterances")
        print("Finished reading training data.")


        headersKore['authorization']=authTokenKore #passing the authorization token to the configBot.py file
        botName=input('Enter Bot Name: ')

        botIdKore, dgValue = ("","")
        if USEKORE:
            botIdKore, dgValue = createKoreBot(botName,userIdKore,authTokenKore,KorePlatform)#Bots creation for Luis and Kore
            print("New bot "+botName+" has been created in Kore with botid: "+ botIdKore)
            prepKore(intentset,intents,utterances,botIdKore,userIdKore,authTokenKore, dgValue)

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
              addIntentAndUtteranceDF(intentset[j],input2[intentset[j]])

        print("Creating the config file for the read.py file.")
        createConfigFile(botName,botIdKore,userIdKore,authTokenKore,KorePlatform,urlL[-1],botIdDF,Token_DF)

def prepLuis(intentset,intents,utterances,botIdLuis):
        print("Creating intents in luis")
        for i in tqdm(range(len(intentset))):
            LuisIntentId.append( addLuisIntent(intentset[i],botIdLuis))#Adding Intent in Luis

        print("Adding train utterances in Luis")
        th=[]
        for i in tqdm(range(len(intents))):
            #addLuisUtterance(utterances[i],LuisIntentId[intentset.index(intents[i])],botIdLuis,intents[i])
            th.append(threading.Thread(target=addLuisUtterance,
                 args=([utterances[i],LuisIntentId[intentset.index(intents[i])],botIdLuis,intents[i]])))
            th[-1].start()
            if not i%10:
                [thread.join() for thread in th]
                th.clear()
            
        print("Fetching the endpoint URL to hit, for Luis, to check response by its bot")           
        urlL.append(getLuisEndPointUrl(botIdLuis))


def prepKore(intentset, intents, utterances,botIdKore,userIdKore,authTokenKore, dgValue):
        print("Creating intents in kore")
        for i in tqdm(range(len(intentset))):
            if "default fallback intent" == intentset[i]:idKore.append(dgValue)
            else:idKore.append(addIntentKore(intentset[i],botIdKore,userIdKore,authTokenKore,KorePlatform))

        th=[]
        print("Adding train utterances in Kore")
        addKoreUtterancesBulk(utterances,botIdKore,intents,userIdKore,authTokenKore,KorePlatform)
        print("training the Kore bot")
        trainKore(botIdKore,userIdKore,authTokenKore,KorePlatform)

def createConfigFile(botName,botIdKore,userIdKore,authTokenKore,KorePlatform,urlL,botIdDF,Token_DF):
	config= {
		"botname_Kore":	botName,
		"uid_Kore":userIdKore,
		"token_Kore":koreClientSecret,
		"streamid_Kore":botIdKore,
		"urlKa":KorePlatform+"/api/",
		"FileName": TestFileName,
		"Token_DF":Token_DF,
		"botname_DF":	botIdDF,
		"urlL":	urlL,
		"USEKORE":USEKORE,
		"USEGOOGLE":USEGOOGLE,
		"USELUIS":USELUIS
		}
	f=open("testconfig.json","w")
	json.dump(config,f, indent=2, ensure_ascii=False,sort_keys=True)
	f.close()

if __name__ == '__main__':
        main()
