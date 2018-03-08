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
def find_intent3(i,ses):
        output=[]
        output.append(TaskNames[i])#In the output, appending the inputs and matched intents to compare with the expected task name
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
        output.append(str(MatchedIntents_Kore[1]))
        output.append(str(MatchedIntents_Kore[2]))    
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
        Utterances.append(row[1])#Reading from the input file i.e. ML_Testdata
        TaskNames.append(row[0].replace("_"," ").lower())
        Types.append(row[2])
    fr.close()
    print("Test data sheet is running")
    timestr=time.strftime("%d-%m-%Y--%H-%M-%S")
    resultsFileName='ML_Results-'+timestr+'.ods'
    fp=open(resultsFileName,'w')
    ods = newdoc(doctype='ods', filename=resultsFileName)
    sheet = Sheet('Results', size=(len(Utterances)+1,12))
    ods.sheets += sheet
    insertRow(sheet,['Expected Task Name','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','Kore Total CS score','Kore ML score','Matched Intent(s) DF','Status','ScoreDF','Matched Intent(s) Luis','Status','ScoresLuis'])
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
                resp=ses.post(config["urlKa"]+config["uid_Kore"]+"/builder/streams/"+config["streamid_Kore"]\
                    +"/findIntent",headers={'authorization':config["token_Kore"]},\
                    json={ "input":input_data,"streamName":config["botname_Kore"]})
                respjson=resp.json()
                resp.raise_for_status()
                break
            except Exception as e:
                print("Error while finding intent kore", e)
                time.sleep(1)

        if respjson and ('response' in respjson) and respjson['response']:
            if ('finalResolver' in respjson['response'].keys()) and respjson['response']["finalResolver"].get("winningIntent",[]):
                matchedIntents_Kore = respjson["response"]["finalResolver"]["ranking"][0]["intent"].replace("_"," ")
                koreMLScore = respjson["response"]["finalResolver"]["ranking"][0]["scoring"]["mlScore"]
                koreCSScore = respjson["response"]["finalResolver"]["ranking"][0]["scoring"]["score"]
            elif ('fm' in respjson['response'].keys()) and respjson['response']["fm"].get("possible",[]):
                matchedIntents_Kore = respjson["response"]["fm"]["possible"][0]["task"].replace("_"," ")
                koreMLScore =respjson["response"]["fm"]["possible"][0]["score"]
                koreCSScore = respjson["response"]["fm"]["possible"][0]["mlScore"]
            elif ('ml' in respjson['response'].keys()) and respjson['response']["ml"].get("possible",[]):
                matchedIntents_Kore = respjson["response"]["ml"]["possible"][0]["task"].replace("_"," ")
                koreMLScore = 'Null'
                koreCSScore = respjson["response"]["ml"]["possible"][0]["score"]
            else:
                matchedIntents_Kore='None'
                koreCSScore='Null'
                koreMLScore='Null'
        else:
            matchedIntents_Kore='None'
            koreCSScore='Null'
            koreMLScore='Null'
        if(matchedIntents_Kore=='Default Fallback Intent'):
                matchedIntents_Kore='None'
        while(len(MatchedIntents_Kore)):
            MatchedIntents_Kore.pop()
        MatchedIntents_Kore.extend([matchedIntents_Kore,koreCSScore,koreMLScore])

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
            matchedIntents_DF='Empty Response Google'
            score=['null']
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
                matchedIntents_Luis='Empty Response Luis'
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


