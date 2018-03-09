import tabulate
import requests, csv, os, time, sys, urllib, json
from threading import Thread
from tqdm import tqdm
from odfhandle import *
'''Three global arrays declared to get input from the ML csv file to get the utterance, expected task name and the type of utterance and 1 array for the output to capture the matched intent and status(success or failure)'''
Utterances=[]
TaskNames=[]
Types=[]
outputs=[]
MatchedIntents_Kore=['','']
MatchedIntents_DF=['','']
MatchedIntents_Luis=['','']
urlDF=		"https://console.dialogflow.com/v1/query"

NUM_THREADS=1
config={}

def printif(*args):
    if config.get("debug", False):
        print(*args)

def find_intent3(i,ses):
        output=[]
        #In the output, appending the inputs and matched intents to compare with the expected task name
        TaskNames[i] = TaskNames[i].replace("\xa0"," ")
        output.append(TaskNames[i])
        output.append(Utterances[i])
        output.append(Types[i])
        thKORE=Thread(target=callKoreBot,args=([Utterances[i], ses[0]]));thKORE.start()
        thDF=Thread(target=callDFBot,args=(Utterances[i],ses[1]));thDF.start()
        thLUIS=Thread(target=callLUISBot,args=(Utterances[i],ses[2]));thLUIS.start()
        thKORE.join();thDF.join();thLUIS.join()
        output.append(MatchedIntents_Kore[0])
        if(MatchedIntents_Kore[0]==TaskNames[i]):
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
        output.append(MatchedIntents_Luis[0])
        if(MatchedIntents_Luis[0]==TaskNames[i]):
                output.append('pass')
        else:
                output.append('fail')
        output.append(str(MatchedIntents_Luis[1]))        
        outputs[i]=output



def main():
    global outputs, config
    MAP=lambda x,y:list(map(x,y))
    ses=MAP(lambda x:MAP(lambda y:y(),x),[[requests.session]*3]*NUM_THREADS)
    config=json.load(open("testconfig.json","r"))
    fr=open(config["FileName"],'r')
    reader=csv.reader(fr,delimiter=',')
    lines=[line for line in reader][1:]
    #reader.next()
    for row in lines:
        if len(row) <=0:
            continue
        if row[0]==None or row[0].strip()=='':
            continue
        TaskName = row[0].replace("_"," ").lower()
        if TaskName == "none":TaskName="None"
        Utterances.append(row[1])
        Types.append(row[2])
        TaskNames.append(TaskName)
    fr.close()
    print("Test data sheet is running")
    timestr=time.strftime("%d-%m-%Y--%H-%M-%S")
    resultsFileName='ML_Results-'+timestr+'.ods'
    fp=open(resultsFileName,'w')
    ods = newdoc(doctype='ods', filename=resultsFileName)
    sheet = Sheet('Results', size=(len(Utterances)+1,14))
    ods.sheets += sheet
    insertRow(sheet,['Expected Task Name','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','Kore Total CS score','Kore ML score','Kore FAQ Score','Matched Intent(s) DF','Status','ScoreDF','Matched Intent(s) Luis','Status','ScoresLuis'])
    ods.save()
    outputs = [None]*len(Utterances)
    th=[]
    prev=0
    for i in tqdm(range(len(Utterances))):
        th.append(Thread(target=find_intent3,args=([i,ses[i%NUM_THREADS]])))
        th[-1].start()
        if i+1==len(Utterances) or (i+1)%NUM_THREADS ==0:
            time.sleep(1)
            MAP(lambda x:x.join(),th)
            # save the contemporary results for safety
            for output in outputs[prev:prev+len(th)]:
                insertRow(sheet,output)
            ods.save()
            prev = prev+len(th)
            th=[]
    ods.save()
    return resultsFileName


def callKoreBot(input_data,ses):
        while(1):
            try:
                resp=ses.post(config["urlKa"]+config["uid_Kore"]+"/builder/streams/"+config["streamid_Kore"]+"/findIntent",
                    headers={'authorization':config["token_Kore"]},
                    json={ "input":input_data,"streamName":config["botname_Kore"]})
                respjson=resp.json()
                if resp.status_code == 400:
                  matchedIntents_Kore = "None"
                  koreMLScore = "Null"
                  koreCSScore = "Null"
                  printif("Null", input_data)
                  break
                resp.raise_for_status()
                break
            except Exception as e:
                print(config["urlKa"]+config["uid_Kore"]+"/builder/streams/"+config["streamid_Kore"]+"/findIntent",
                    {'authorization':config["token_Kore"]},
                    { "input":input_data,"streamName":config["botname_Kore"]})
                print("Error while finding intent kore", e)
                time.sleep(1)

        if respjson and ('response' in respjson) and respjson['response']:
            if ('finalResolver' in respjson['response'].keys()) and respjson['response']["finalResolver"].get("winningIntent",[]):
                rankedMaxScore = 0.0
                rankedMaxObj = respjson["response"]["finalResolver"]["ranking"][0]
                for rankedObj in respjson["response"]["finalResolver"]["ranking"]:
                    rankedScore = rankedObj["totalScore"]
                    if rankedScore > rankedMaxScore:
                       rankedMaxScore = rankedScore
                       rankedMaxObj = rankedObj
                matchedIntents_Kore = rankingMaxObj["intent"].replace("_"," ").lower()
                if "scoring" in rankingMaxObj:
                    koreMLScore = rankingMaxObj["scoring"].get("mlScore",0.0)
                    koreCSScore = rankingMaxObj["scoring"].get("score",0.0)
                    koreFAQScore = rankingMaxObj["scoring"].get("faqScore",0.0)
                else:
                    koreMLScore = rankingMaxObj("mlScore", 0.0)
                    koreCSScore = rankingMaxObj(score, 0.0)
                    koreFAQScore = rankingMaxObj.get("faqScore", 0.0)
            elif ('fm' in respjson['response'].keys()) and respjson['response']["fm"].get("possible",[]):
                matchedIntents_Kore = respjson["response"]["fm"]["possible"][0]["task"].replace("_"," ").lower()
                koreMLScore = respjson["response"]["fm"]["possible"][0]["mlScore"]
                koreCSScore = respjson["response"]["fm"]["possible"][0]["score"]
                koreFAQScore = respjson["response"]["fm"]["possible"][0].get("faqScore",0.0)
            elif ('ml' in respjson['response'].keys()) and respjson['response']["ml"].get("possible",[]):
                matchedIntents_Kore = respjson["response"]["ml"]["possible"][0]["task"].replace("_"," ").lower()
                koreMLScore = respjson["response"]["ml"]["possible"][0]["score"]
                koreCSScore = 0.0
                koreFAQScore = 0.0
            elif ('faq' in respjson['response'].keys()) and respjson['response']["faq"].get("possible",[]):
                matchedIntents_Kore = respjson["response"]["faq"]["definitive"]["task"].replace("_"," ").lower()
                koreMLScore = 0.0
                koreCSScore = 0.0
                koreFAQScore = respjson["response"]["faq"]["definitive"]["faqScore"]
            else:
                matchedIntents_Kore='None'
                koreCSScore='Null'
                koreMLScore='Null'
                koreFAQScore = 'Null'
                printif("NULL2",input_data)
        else:
            printif("NULL3",input_data)
            matchedIntents_Kore='None'
            koreCSScore='Null'
            koreMLScore='Null'
            koreFAQScore = 'Null'
        if(matchedIntents_Kore=='Default Fallback Intent'.lower()):
                matchedIntents_Kore='None'
        while(len(MatchedIntents_Kore)):
            MatchedIntents_Kore.pop()
        MatchedIntents_Kore.extend([matchedIntents_Kore,koreCSScore,koreMLScore, koreFAQScore])

def callDFBot(input_data,ses):
    if config["USEGOOGLE"]:
        query=urllib.parse.quote(input_data.replace("!",""))
        params = {
		"query":query,
		"lang":"en",
		"sessionId":config["botname_DF"],
		"timezone":"UTC"
		}
        headers = {"authorization": "Bearer "+config["Token_DF"]}
        while(1):
            try:
                response = ses.get( urlDF,  headers=headers,params=params)
                response.raise_for_status()
                responsejson = response.json()
                break
            except Exception as e:
                print("Error while finding intent in google", e)
                print("GOOGLE","get", urlDF, "headers=",headers,"params",params)
                time.sleep(1)
        if not responsejson=={} and ('result' in responsejson) and ('metadata' in responsejson['result']) and ('intentName' in responsejson['result']['metadata']):
            matchedIntents_DF=responsejson['result']['metadata']['intentName'].lower()
            score=responsejson['result']['score']#Getting the confidence score.
            if(matchedIntents_DF=='Default Fallback Intent'):
                matchedIntents_DF='None'
        else:
            matchedIntents_DF='None'
            score='null'
            print("GOOGLE","get", urlDF, "headers=",headers,"params",params)
    else:
        matchedIntents_DF='None'
        score=0.1
    while(MatchedIntents_DF):
        MatchedIntents_DF.pop()
    MatchedIntents_DF.extend([matchedIntents_DF,score])
            
def callLUISBot(input_data,ses):
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
                if respluis['topScoringIntent']['intent']=='None':
                        matchedIntents_Luis='None'
        else:
                matchedIntents_Luis='None'
                score='Null'
                print("LUIS","get" , (config["urlL"]+input_data))
                print(respLuis)
    else:
        matchedIntents_Luis='None'
        score=0.1
    while(len(MatchedIntents_Luis)):
        MatchedIntents_Luis.pop()
    MatchedIntents_Luis.extend([matchedIntents_Luis,score])

if __name__ == "__main__":
    if len(sys.argv) ==1:
        start_time=time.time()
        resultsFileName=main()
        print(time.time()-start_time)
        print(resultsFileName)
    ods = opendoc(filename=resultsFileName)
    tabulate.main(ods)


