import requests, csv, os, time, sys, threading, getpass, json ,copy
from six.moves import input
from configBot import *
from tqdm import tqdm
from googleDF import *
from kore import *
from luis import *
from watson import *
import wit

#Global varibles used for reading input from the csv file
intents=[]
utterances=[]
loginResp=[]
urlL=[""]
input2={}
intentset=[]
idKore=[]
LuisIntentId=[]
KorePublicApi = False


def main():
        fr=open(fileName,'r')
        reader=csv.reader(fr,delimiter=',')
        for row in reader:
                if len(row)<=0:
                        continue
                row[0] =row[0].strip().lower().replace("-","").replace("_"," ")
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


        global authTokenKore, userIdKore
        botIdKore, dgValue = ("","")
        if USEKORE:
            if ssoKore is False:
                authTokenKore,userIdKore = loginToKore(KoreEmailId, KorePassword, KorePlatform)

            headersKore['authorization']=authTokenKore #passing the authorization token to the configBot.py file
            botIdKore, dgValue = createKoreBot(botName,userIdKore,authTokenKore,KorePlatform,KorePublicApi)
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
        '''
        for i in range(len(intentset)):
            input2[intentset[i]]=[]

        for i in range(len(intents)):
            input2[intents[i]].append(utterances[i])

        if USEGOOGLE:
          print("Training Google bot after collecting all the train utterances")
          for j in tqdm(range(len(intentset))):
              addIntentAndUtteranceDF(intentset[j],input2[intentset[j]])

        if USEWATSON:
          print("Create Watson workspace")
          watsonBotId = WatsonCreateBot(botName)
          print("Adding intents and train utterances")
          for j in tqdm(range(len(intentset))):
              WatsonAddIntentAndUtterance(watsonBotId, intentset[j],input2[intentset[j]])
        else:
          watsonBotId=""
        if USEWIT:
          witSession = requests.Session()
          print("Create Wit bot")
          witBotId, witBotToken, witIntentId, witSemanticTagsId  = wit.createBot(witSession, botName,lang=lang)
          #print("Adding intents")
          print("Adding intents and train utterances")
          for j in tqdm(range(len(intentset))):
              wit.addIntentToBot(witSession, witBotId, witSemanticTagsId, intentset[j])
              wit.addUtterances(witSession, witBotId, witIntentId, witSemanticTagsId, input2[intentset[j]], intentset[j])
          #print("Adding train utterances")
        else:
          witBotToken=""
'''
        print("Creating the config file (testconfig.json) for the runTest.py file.")
        createConfigFile(botName,botIdKore,userIdKore,authTokenKore,KorePlatform,urlL[0],botIdDF,Token_DF,watsonBotId,witBotToken)

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
        urlL[0]= getLuisEndPointUrl(botIdLuis)


def prepKore(intentset, intents, utterances,botIdKore,userIdKore,authTokenKore, dgValue):
        print("Creating intents in kore")
        intents_copy = copy.deepcopy(intents)
        for i,val in enumerate(intents):
            intents[i] = intents[i].replace(",","").replace("?","").replace("'","").replace("."," ").replace("/","")
            if "None" == WatsonCleanIntent(intents[i]):idKore.append(dgValue)
            else:idKore.append(addIntentKore(intents[i],botIdKore,userIdKore,authTokenKore,KorePlatform,utterances[i]))
        th=[]
        #print("Adding train utterances in Kore")
        addKoreUtterancesBulk(intents_copy,botIdKore,intents,userIdKore,authTokenKore,KorePlatform)
        #print("waiting on intermediate training of the Kore bot to finish")
        #trainKore(botIdKore,userIdKore,authTokenKore,KorePlatform)
        #print("Training of the Kore bot with full Data")
        #trainKore(botIdKore,userIdKore,authTokenKore,KorePlatform)

def createConfigFile(botName,botIdKore,userIdKore,authTokenKore,KorePlatform,urlL,botIdDF,Token_DF,watsonBotId,witBotToken):
	config= {
		"botname_Kore":	botName,
		"uid_Kore":userIdKore,
		"streamid_Kore":botIdKore,
		"urlKa":KorePlatform,
		"KorePublicApi":KorePublicApi,
		"FileName": TestFileName,
		"Token_DF":Token_DF,
		"botname_DF":	botIdDF,
		"urlL":	urlL,
		"USEKORE":USEKORE,
		"USEGOOGLE":USEGOOGLE,
		"USELUIS":USELUIS,
		"USEWATSON":USEWATSON,
		"watsonBotId":watsonBotId,
		"USEWIT":USEWIT,
		"witBotToken":witBotToken,
		"lang":lang,
		"RESULTSFILE":RESULTSFILE,
                "threshold" : threshold
		}
	if config["KorePublicApi"]:config["token_Kore"] = koreClientSecret
	else:config["token_Kore"] = authTokenKore
	f=open("testconfig.json","w")
	json.dump(config,f, indent=2, ensure_ascii=False,sort_keys=True)
	f.close()

if __name__ == '__main__':
        main()
