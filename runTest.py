import tabulate
import requests, csv, os, time, sys, urllib, json, base64, hashlib, hmac
from threading import Thread
from tqdm import tqdm
# from watson import *
from odfhandle import *
from configBot import *
from cx import getAgent, detect_intent
'''Three global arrays declared to get input from the ML csv file to get the utterance, expected task name and the type of utterance and 1 array for the output to capture the matched intent and status(success or failure)'''
Utterances=[]
TaskNames=[]
Types=[]
outputs=[]
urlDF="https://api.dialogflow.com/v1/query"

NUM_THREADS=3
config={}
dfAgent={}

def printif(*args):
    return
    if config.get("debug", False):
        print(*args)

#tqdm = lambda x:x

def getJWT(clientSecret): # should be modified, need not be used
	ID = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
	dig = hmac.new(clientSecret.encode("utf-8"), msg=ID.encode("utf-8"), digestmod=hashlib.sha256).digest()
	H=base64.urlsafe_b64encode(dig).decode()
	return ID+"."+H[:-1]

def find_intent3(sheet,i,ses):
        MatchedIntents_Kore=['None','Null','Null','Null']
        MatchedIntents_DF=['None','Null']
        MatchedIntents_Luis=['None','Null']
        MatchedIntents_Watson=['None','Null','Null']
        output=[]
        #In the output, appending the inputs and matched intents to compare with the expected task name
        TaskNames[i] = TaskNames[i].replace("\xa0"," ")
        output.append(TaskNames[i])
        output.append(Utterances[i])
        output.append(Types[i])
        thKORE=Thread(target=callKoreBot,args=(MatchedIntents_Kore,Utterances[i], ses[0]));thKORE.start()
        thDF=Thread(target=callDFBot,args=(MatchedIntents_DF,Utterances[i],ses[1],dfAgent.get("name")));thDF.start()
        # thLUIS=Thread(target=callLUISBot,args=(MatchedIntents_Luis,Utterances[i],ses[2]));thLUIS.start()
        # thWatson=Thread(target=callWatsonBot,args=(MatchedIntents_Watson,Utterances[i],ses[3]));thWatson.start()
        thKORE.join();thDF.join();#thLUIS.join();thWatson.join()
        output.append(MatchedIntents_Kore[0])
        if MatchedIntents_Kore[0]==TaskNames[i]:
            output.append('pass')
        elif MatchedIntents_Kore[0][:10]=='Ambiguity:' and TaskNames[i]=='None':
            output.append('pass')
        else:
            output.append('fail')
        output.append(str(MatchedIntents_Kore[1])) # CS score
        output.append(str(MatchedIntents_Kore[2])) # ML score
        output.append(str(MatchedIntents_Kore[3])) # FAQ score
        output.append(MatchedIntents_DF[0])
        if(MatchedIntents_DF[0]==TaskNames[i]):
            output.append('pass')
        else:
            output.append('fail')
        output.append(str(MatchedIntents_DF[1]))

        # output.append(MatchedIntents_Luis[0])
        # if(MatchedIntents_Luis[0]==TaskNames[i]):
        #         output.append('pass')
        # else:
        #         output.append('fail')
        # output.append(str(MatchedIntents_Luis[1]))

        # output.append(MatchedIntents_Watson[0])
        # if(MatchedIntents_Watson[0]==WatsonCleanIntent(TaskNames[i])):
        #         output.append('pass')
        # else:
        #         output.append('fail')
        # output.append(str(MatchedIntents_Watson[1]))

        # save the contemporary results for safety
        replaceRow(sheet,output,i+1)
        time.sleep(1)

def main():
    global outputs, config, dfAgent
    MAP=lambda x,y:list(map(x,y))
    ses=MAP(lambda x:MAP(lambda y:y(),x),[[requests.session]*4]*NUM_THREADS)
    th=[None]*NUM_THREADS
    config=json.load(open(sys.argv[1],"r"))
    if USEGOOGLE:
        dfAgent = getAgent(botName)
    fr=open(config["FileName"],'r')
    reader=csv.reader(fr,delimiter=',')
    lines=[line for line in reader][1:]
    for row in lines:
        if len(row) <=0:
            continue
        if row[0]==None or row[0].strip()=='':
            continue
        TaskName = row[0].replace("_"," ").replace("-","").lower()
        if TaskName == "none":TaskName="None"
        Utterances.append(row[1])
        Type = "Positive"
        if len(row) == 3: Type = row[2]
        Types.append(Type)
        TaskNames.append(TaskName)
    fr.close()
    print("Test data sheet is running")
    timestr=time.strftime("%d-%m-%Y--%H-%M-%S")
    if config.get("RESULTSFILE",""):
        resultsFileName=config["RESULTSFILE"]
    else:
        resultsFileNameDef="ML_Results-"+config["botname_Kore"]+"-"+timestr+".ods"
        resultsFileName = input("Enter resultsFileName(default:"+resultsFileNameDef+"):")
        if not resultsFileName:resultsFileName=resultsFileNameDef
        if not resultsFileName.split(".")[-1] == "ods": resultsFileName += ".ods"
    ods = newdoc(doctype='ods', filename=resultsFileName)
    sheet = Sheet('Results', size=(len(Utterances)+1,18))
    ods.sheets += sheet
    insertRow(sheet,['Expected Task Name','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','Kore Total CS score','Kore ML score','Kore FAQ Score','Matched Intent(s) DF','Status','ScoreDF'])
    ods.save()
    outputs = [None]*len(Utterances)
    prev=0
    for i in tqdm(range(len(Utterances))):
        while len([x for x in th if x]) == NUM_THREADS:
            for x in th:
                if x and not x.isAlive():
                  x.join()
                  th[th.index(x)]=None
            time.sleep(0.1)
        for j in range(len(th)):
          if th[j] == None:
            break
        ods.save()
        if j == len(th):input("j==len th!!! How can this be?!")
        th[j] = Thread(target=find_intent3,args=([sheet,i,ses[j]]))
        th[j].start()
        if i+1==len(Utterances):
            for x in th:
              if x:x.join()
    ods.save()
    return resultsFileName

def callWatsonBot(MatchedIntents_Watson, input_data, ses):
        if config["USEWATSON"]:
	        # ses is unused for now.
	        resp = WatsonFindIntent(config["watsonBotId"], input_data)
	        MatchedIntents_Watson.clear()
	        MatchedIntents_Watson.extend([resp[0]["intent"],resp[0]["confidence"], json.dumps(resp)])

def callKoreBot(MatchedIntents_Kore, input_data,ses):
        if config["KorePublicApi"]:
            jwtToken = getJWT(config["token_Kore"])
            koreUrl=config["urlKa"]+"/api/v1.1/rest/streams/"+config["streamid_Kore"]+"/findIntent"
            headers={'auth':jwtToken}
        else:
            koreUrl=config["urlKa"]+"/api/1.1/users/"+config["uid_Kore"]+"/builder/streams/"+config["streamid_Kore"]+"/findIntent"
            headers={'authorization':config["token_Kore"], "bot-language":lang}
        respjson={}
        loops = 0
        while(config["USEKORE"]):
            if loops > 20:
                print("Max retries exceeded for utterance\n"+input_data)
                break
            loops += 1
            try:
                code = 1
                while code == 401 or code == 1 or code == 504:
                  if code == 504:time.sleep(3)
                  if code == 401:
                    config["token_Kore"] = str(input(resp.text+"\nplease enter new kore token:"))
                    code=1

                  resp=ses.post(koreUrl, headers=headers,json={ "input":input_data,"streamName":config["botname_Kore"]})
                  if resp.status_code == 400:
                    matchedIntents_Kore = "None"
                    koreMLScore = "Null"
                    koreCSScore = "Null"
                    printif("Null", input_data)
                    break
                  code = resp.status_code
                if resp.status_code==400:
                    print("exception resp 400")
                    break
                resp.raise_for_status()
                respjson=resp.json()
                break
            except Exception as e:
                print(koreUrl,
                    {'authorization':config["token_Kore"]},
                    { "input":input_data,"streamName":config["botname_Kore"]})
                print("Error while finding intent kore", e)
                time.sleep(1)

        if respjson and ('response' in respjson) and respjson['response']:
            if ('finalResolver' in respjson['response'].keys()) and respjson['response']["finalResolver"].get("winningIntent",[]):
              result = respjson["response"].get("result", respjson.get("result", "failintent"))
              if len(respjson['response']["finalResolver"].get("winningIntent",[]))==1 and result=="successintent":
                matchedIntents_Kore = respjson['response']["finalResolver"]["winningIntent"][0]["intent"].replace("_"," ").lower()
                rankingMaxObj = {}
                for rankingObj in respjson["response"]["finalResolver"]["ranking"]:
                    if matchedIntents_Kore == rankingObj["intent"].replace("_"," ").lower():
                       rankingMaxObj = rankingObj
                if "scoring" in rankingMaxObj:
                    koreMLScore = rankingMaxObj["scoring"].get("mlScore",0.0)
                    koreCSScore = rankingMaxObj["scoring"].get("score",0.0)
                    koreFAQScore = rankingMaxObj["scoring"].get("faqScore",0.0)
                else:
                    koreMLScore = rankingMaxObj.get("mlScore", 0.0)
                    koreCSScore = rankingMaxObj.get("score", 0.0)
                    koreFAQScore = rankingMaxObj.get("faqScore", 0.0)
                    if not rankingMaxObj:
                        koreMLScore = respjson['response']["finalResolver"]["winningIntent"][0].get("score", 0.0)
              else:
                matchedIntents_Kore="Ambiguity:"
                koreCSScore  = 0.0
                koreMLScore  = 0.0
                koreFAQScore = 0.0
                for winningObj in respjson['response']["finalResolver"]["winningIntent"]:
                    matchedIntents_Kore+=winningObj.get("intent","").replace("_"," ").lower()+"|"
                matchedIntents_Kore=matchedIntents_Kore[:-1]
            else:
                matchedIntents_Kore = "None"
                koreCSScore  = 0.0
                koreMLScore  = 0.0
                koreFAQScore = 0.0
        else:
            printif("NULL3",input_data)
            matchedIntents_Kore='None'
            koreCSScore='Null'
            koreMLScore='Null'
            koreFAQScore = 'Null'
        if(matchedIntents_Kore=='Default Fallback Intent'.lower()):
                matchedIntents_Kore='None'
        MatchedIntents_Kore.clear()
        MatchedIntents_Kore.extend([matchedIntents_Kore,koreCSScore,koreMLScore, koreFAQScore])

def callDFBot(MatchedIntents_DF, input_data,ses,agent):
    if config["USEGOOGLE"]:
        # query=urllib.parse.quote(input_data.replace("!",""))
        # querystring = {"v":"20150910","contexts":"shop","lang":lang,"query":query,"sessionId":"12345","timezone":"America/New_York"}
        # params=querystring
        # headers = {
        #     'Authorization': "Bearer "+ Client_DF, #config["DF_CLIENT_ACCESS_TOKEN"],
        #     'cache-control': "no-cache",
        #     'Postman-Token': "acfe1c90-1266-455f-96e6-2fbc759e115b"
        #     }
        count = 0
        while(1):
            count = count +1
            try:
                actual_intent,confidence_score = detect_intent(agent, input_data)
                break
            except Exception as e:
                print(e)
                #time.sleep(11)
                print("Error while finding intent in google", e)
                if count > 3:
                    break
                time.sleep(1)
        if actual_intent:
            matchedIntents_DF=actual_intent.lower()
            score=confidence_score
            if(matchedIntents_DF=='Default Fallback Intent'):
                matchedIntents_DF='None'
        else:
            matchedIntents_DF='None'
            score='null'
            print("null score google")
    else:
        matchedIntents_DF='None'
        score=0
    MatchedIntents_DF.clear()
    MatchedIntents_DF.extend([matchedIntents_DF,score])
            
def callLUISBot(MatchedIntents_Luis,input_data,ses):
    if config["USELUIS"]:
        while(1):
            try:
                respLuis=ses.get(config["urlL"]+input_data)#Reading the JSON response for luis.ai
                respLuis.raise_for_status()
                respluis=respLuis.json()
                break
            except Exception as e:
                print("Error while finding intent in Luis", e)
                time.sleep(1)
        if respluis!={} and ('topScoringIntent' in respluis) and ('intent' in respluis['topScoringIntent']):
                matchedIntents_Luis=respluis['topScoringIntent']['intent'].lower()#Luis Output Taken Here
                score=respluis['topScoringIntent']['score']#Getting Luis Score
                if respluis['topScoringIntent']['intent']=='None' or score < config['threshold']:
                        matchedIntents_Luis='None'
        else:
                matchedIntents_Luis='None'
                score='Null'
                print("LUIS","get" , (config["urlL"]+input_data))
                print(respLuis)
    else:
        matchedIntents_Luis='None'
        score=0.1
    MatchedIntents_Luis.clear()
    MatchedIntents_Luis.extend([matchedIntents_Luis,score])

if __name__ == "__main__":
    if len(sys.argv) !=2:
        print("Usage: python read.py <testconfig file>")
        exit()
    start_time=time.time()
    resultsFileName=main()
    print("Time elapsed for testing",time.time()-start_time)
    print(resultsFileName)
    ods = opendoc(filename=resultsFileName)
    tabulate.main(ods)


