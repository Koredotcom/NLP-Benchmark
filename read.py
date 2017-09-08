import tabulate
import requests, csv, os, time, sys, threading
from tqdm import tqdm
from config import *     #Calling the config file which contains all the static variables used in the code
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

def find_intent3(i):
        output=[]
        output.append(TaskNames[i])#In the output, appending the inputs and matched intents to compare with the expected task name
        output.append(Utterances[i])
        output.append(Types[i])
        thKORE=threading.Thread(target=callKoreBot,args=([token_QAbots, Utterances[i]]));thKORE.start()
        thAPI=threading.Thread(target=callAPIBot,args=([Utterances[i]]));thAPI.start()
        thLUIS=threading.Thread(target=callLUISBot,args=([Utterances[i]]));thLUIS.start()
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
        outputs.append(output)

def main():
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
    fp=open(resultsFileName,'w')
    fp.write(",".join(['Expected Task Name','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','Kore Total CS score','Kore ML score','Matched Intent(s) API','Status','ScoreApi','Matched Intent(s) Luis','Status,ScoresLuis']) + '\n')
    th=[]
    for i in tqdm(range(len(Utterances))):
        th.append(threading.Thread(target=find_intent3,args=([i])))
        th[i].start()
        if i%10 ==0:
            time.sleep(1)
            map(lambda x:x.join(),th[0:i])
    map(lambda x:x.join(),th[0:-1])
    th[-1].join()
    for output in outputs:
        fp.write(','.join(output) + '\n')#Printing the output results
    fp.close()
    return resultsFileName


def callKoreBot(token_QAbots, input_data):
        while(1):
            try:
                resp=requests.post(urlKa+uid_QAbots+urlKb+streamid_QAbots+urlKc,headers={'authorization':token_QAbots},\
                    data={ "input":input_data,"streamName":botname_QAbots})#Hitting find intent API call for kore.ai
                respjson=resp.json()
                resp.raise_for_status()
                break
            except:
                print("Error while finding intent kore")
                time.sleep(1)

        url = urlKa+uid_QAbots+urlKb+streamid_QAbots+"/getTrainLogs"#Hitting the trainLogs api for kore to get the CS score and the ML Score
        querystring = {"rnd":"6ye6to"}
        payload = "{\"input\":\""+input_data+"&#160;\",\"streamName\":\""+botname_QAbots+"\"}"
        headers = {
    'authorization': token_QAbots,
    'content-type': "application/json;charset=UTF-8",
            }
        while(1):
            try:
                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
                response.raise_for_status()
                break
            except:
                print("Error while finding trainlogs kore")
                time.sleep(1)
            
        if not respjson=={} and respjson.has_key('intent') and not respjson['intent'] ==[] and not respjson['intent']==None and respjson['intent'][0].has_key('name'):
            matchedIntents_qabots=respjson['intent'][0]['name']
            if(response.json()['response']['intentMatch']==[]):
                koreCSScore='Null'
                koreMLScore='Null'
            else:
                try:
                    koreCSScore=response.json()['response']['intentMatch'][0]['totalScore']#Getting CS Score
                except:
                    koreCSScore='Null'
                try:
                    koreMLScore=response.json()['response']['intentMatch'][0]['mlScore']#Getting ML Score              
                except:    
                    koreMLScore='Null'              

        else:
            matchedIntents_qabots='None'
            koreCSScore='Null'
            koreMLScore='Null'
        if(matchedIntents_qabots=='Default Fallback Intent'):
                matchedIntents_qabots='None'
        while(len(MatchedIntents_qabots)):
            MatchedIntents_qabots.pop()
        MatchedIntents_qabots.extend([matchedIntents_qabots,koreCSScore,koreMLScore])

def callAPIBot(input_data):
    if USEGOOGLE:
        payload = {"q":input_data,"lang":"en","sessionId":botname_API}
        payload=str(payload)
        headers = {
        'authorization': "Bearer "+Token_Api,
        'content-type': "application/json",
         }
        while(1):
            try:
                response = requests.request("post", url, data=payload, headers=headers)#Hitting the API call for api.ai
                response.json()
                #response.raise_for_status()
                break
            except:
                time.sleep(1)
                print("Error while finding intent in google")

        if not response.json()=={} and response.json().has_key('result') and response.json()['result'].has_key('metadata') and response.json()['result']['metadata'].has_key('intentName'):
            matchedIntents_Api=response.json()['result']['metadata']['intentName']
            score=response.json()['result']['score']#Getting the confidence score.
        else:
            matchedIntents_Api='None'
            score=['null']
    
        if(matchedIntents_Api=='Default Fallback Intent'):
            matchedIntents_Api='None'        
    else:
        matchedIntents_Api='None'        
        score=0.1
    while(len(MatchedIntents_Api)):
        MatchedIntents_Api.pop()
    MatchedIntents_Api.extend([matchedIntents_Api,score])
            
def callLUISBot(input_data):
    if USELUIS:
        while(1):
            try:
                respLuis=requests.get(urlL+input_data)#Reading the JSON response for luis.ai
                respluis=respLuis.json()
                #respLuis.raise_for_status()
                break
            except:
                print("Error while finding intent in Luis")
                time.sleep(1)
        if respluis!={} and respluis.has_key('topScoringIntent') and respluis['topScoringIntent'].has_key('intent') and respluis['topScoringIntent']['intent']!='None':
                matchedIntents_Luis=respluis['topScoringIntent']['intent']#Luis Output Taken Here
                score=respluis['topScoringIntent']['score']#Getting Luis Score
        else:         
                matchedIntents_Luis='None'
                score='Null'
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
    tabulate.main(resultsFileName)


