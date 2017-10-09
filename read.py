import tabulate
import requests, csv, os, time, sys, urllib
from threading import Thread
from tqdm import tqdm
from config import *     #Calling the config file which contains all the static variables used in the code
from odfhandle import *
reload(sys)
sys.setdefaultencoding('utf8')
'''Three global arrays declared to get input from the ML csv file to get the utterance, expected task name and the type of utterance and 1 array for the output to capture the matched intent and status(success or failure)'''
Utterances=[]
TaskNames=[]
Types=[]
outputs=[]
MatchedIntents_qabots=['','']
MatchedIntents_Api=['','']
MatchedIntents_Luis=['','']
NUM_THREADS=1 # integer, >=1

def find_intent3(i,ses):
        output=[]
        output.append(TaskNames[i])#In the output, appending the inputs and matched intents to compare with the expected task name
        output.append(Utterances[i])
        output.append(Types[i])
        thKORE=Thread(target=callKoreBot,args=([token_QAbots, Utterances[i], ses[0]]));thKORE.start()
        thAPI=Thread(target=callAPIBot,args=([Utterances[i]],ses[1]));thAPI.start()
        thLUIS=Thread(target=callLUISBot,args=([Utterances[i]],ses[2]));thLUIS.start()
        thKORE.join();thAPI.join();thLUIS.join()
        output.append(MatchedIntents_qabots[0])
        if(MatchedIntents_qabots[0]==TaskNames[i]):
            output.append('pass')
        else:
            output.append('fail')
        output.append(str(MatchedIntents_qabots[1]))
        output.append(str(MatchedIntents_qabots[2]))    
        output.append(MatchedIntents_Api[0])
        if(MatchedIntents_Api[0]==TaskNames[i]):
            output.append('pass')
        else:
            output.append('fail')
        output.append(str(MatchedIntents_Api[1]))    
        output.append(MatchedIntents_Luis[0])
        if(MatchedIntents_Luis[0]==TaskNames[i]):
                output.append('pass')
        else:
                output.append('fail')
        output.append(str(MatchedIntents_Luis[1]))        
        outputs[i]=output



def main():
    global outputs
    ses=map(lambda x:map(lambda y:y(),x),[[requests.session]*3]*NUM_THREADS)
    fr=open(FileName,'r')
    reader=csv.reader(fr,delimiter=',')
    reader.next()
    for row in reader:
        if len(row) <=0:
            continue
        if row[0]==None or row[0].strip()=='':
            continue
        Utterances.append(row[1])#'''Reading from the input file i.e. ML_Testdata'''
        TaskNames.append(row[0].replace("_"," "))
        Types.append(row[2])
    fr.close()
    print("Test data sheet is running")
    timestr=time.strftime("%d-%m-%Y--%H-%M-%S")
    resultsFileName='ML_Results-'+timestr+'.csv'
    resultsFileName="tmp.ods"
    #fp=open(resultsFileName,'w')
    ods = newdoc(doctype='ods', filename=resultsFileName)
    sheet = Sheet('Results', size=(len(Utterances)+1,12))
    ods.sheets += sheet
    insertRow(sheet,['Expected Task Name','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','Kore Total CS score','Kore ML score','Matched Intent(s) API','Status','ScoreApi','Matched Intent(s) Luis','Status,ScoresLuis'])
    ods.save()
    outputs = [None]*len(Utterances)
    th=[]
    prev=0
    for i in tqdm(range(len(Utterances))):
        th.append(Thread(target=find_intent3,args=([i,ses[i%NUM_THREADS]])))
        th[-1].start()
        if i+1==len(Utterances) or (i+1)%NUM_THREADS ==0:
            map(lambda x:x.join(),th)
            # save the contemporary results for safety
            for output in outputs[prev:prev+len(th)]:
                insertRow(sheet,output)
            ods.save()
            prev = prev+len(th)
            th=[]
    ods.save()
    return resultsFileName


def callKoreBot(token_QAbots, input_data,ses):
        while(1):
            try:
                resp=ses.post(urlKa+uid_QAbots+urlKb+streamid_QAbots+urlKc,headers={'authorization':token_QAbots},\
                    data={ "input":input_data,"streamName":botname_QAbots})#Hitting find intent API call for kore.ai
                respjson=resp.json()
                resp.raise_for_status()
                break
            except Exception as e:
                print("Error while finding intent kore", e)
                time.sleep(1)

        url = urlKa+uid_QAbots+urlKb+streamid_QAbots+"/getTrainLogs"#Hitting the trainLogs api for kore to get the CS score and the ML Score
        querystring = {"rnd":"6ye6to"}
        payload = "{\"input\":\""+input_data+"&#160;\",\"streamName\":\""+botname_QAbots+"\"}"
        headers = {
    'authorization': token_QAbots,
    'content-type': "application/json;charset=UTF-8",
            }
        responsejson=respjson

        if not respjson=={} and respjson.has_key('intent') and not respjson['intent'] ==[] and not respjson['intent']==None and respjson['intent'][0].has_key('name'):
            matchedIntents_qabots=respjson['intent'][0]['name']
            if(responsejson['response']['intentMatch']==[]):
                koreCSScore='Null'
                koreMLScore='Null'
            else:
                try:
                    koreCSScore=responsejson['response']['intentMatch'][0]['totalScore']#Getting CS Score
                except:
                    koreCSScore='Null'
                try:
                    koreMLScore=responsejson['response']['intentMatch'][0]['mlScore']#Getting ML Score
                except:    
                    koreMLScore='Null'              

        else:
            matchedIntents_qabots='Empty Response Kore'
            koreCSScore='Null'
            koreMLScore='Null'
        if(matchedIntents_qabots=='Default Fallback Intent'):
                matchedIntents_qabots='None'
        while(len(MatchedIntents_qabots)):
            MatchedIntents_qabots.pop()
        MatchedIntents_qabots.extend([matchedIntents_qabots,koreCSScore,koreMLScore])

def callAPIBot(input_data,ses):
    if USEGOOGLE:
        payload = {"q":input_data,"timezone":"UTC","lang":"en","sessionId":botname_API,"resetContexts":False}
        payload=str(payload)
	params = {
		"query":urllib.quote(input_data.replace("!","")),
		"lang":"en",
		"sessionId":botname_API,
		"timezone":"UTC",
		}
        headers = {
        'authorization': "Bearer "+Token_Api,
        'cache-control':'no-cache',
        'content-type': "application/json;charset=utf8",
         }
        while(1):
            try:
                #response = ses.post( url, data=payload, headers=headers,params = {"v":"20150910"})
                response = ses.get( url,  headers=headers,params=params)
		#Hitting the API call for api.ai
                response.json()
                response.raise_for_status()
                break
            except Exception as e:
                print("Error while finding intent in google", e)
                time.sleep(1)
        responsejson = response.json()
        if not responsejson=={} and responsejson.has_key('result') and responsejson['result'].has_key('metadata') and responsejson['result']['metadata'].has_key('intentName'):
            matchedIntents_Api=responsejson['result']['metadata']['intentName']
            score=responsejson['result']['score']#Getting the confidence score.
            if(matchedIntents_Api=='Default Fallback Intent'):
                matchedIntents_Api='None'
        else:
            matchedIntents_Api='Empty Response Google'
            score=['null']
            #print("GUGL","post", url, "data=",payload, "headers=",headers)
            print("GOOGLE","get", url, "headers=",headers,"params",params)
    else:
        matchedIntents_Api='None'
        score=0.1
    while(MatchedIntents_Api):
        MatchedIntents_Api.pop()
    MatchedIntents_Api.extend([matchedIntents_Api,score])
            
def callLUISBot(input_data,ses):
    if USELUIS:
        while(1):
            try:
                respLuis=ses.get(urlL+input_data)#Reading the JSON response for luis.ai
                respluis=respLuis.json()
                respLuis.raise_for_status()
                break
            except Exception as e:
                print("Error while finding intent in Luis", e)
                time.sleep(1)
        if respluis!={} and respluis.has_key('topScoringIntent') and respluis['topScoringIntent'].has_key('intent'):
                matchedIntents_Luis=respluis['topScoringIntent']['intent']#Luis Output Taken Here
                score=respluis['topScoringIntent']['score']#Getting Luis Score
                if respluis['topScoringIntent']['intent']=='None':
                        matchedIntents_Luis='None'
        else:
                matchedIntents_Luis='Empty Response Luis'
                score='Null'
                print("LUIS","get" , (urlL+input_data))
		print(respLuis)
    else:
        matchedIntents_Luis='None'
        score=0.1
    while(len(MatchedIntents_Luis)):
        MatchedIntents_Luis.pop()
    MatchedIntents_Luis.extend([matchedIntents_Luis,score])

if __name__ == "__main__":
    start_time=time.time()
    resultsFileName=main()
    print(time.time()-start_time)
#    tabulate.main(resultsFileName)


