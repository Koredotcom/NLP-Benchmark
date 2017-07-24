import tabulate
import requests, csv, os, time,sys,urllib
from tqdm import tqdm
from config import *     #Calling the config file which contains all the static variables used in the code'''
reload(sys)
sys.setdefaultencoding('utf8')
'''Three global arrays declared to get input from the ML csv file to get the utterance, expected task name and the type of utterance and 1 array for the output to capture the matched intent and status(success or failure)'''
Utterances=[]
TaskNames=[]
Types=[]
outputs=[]
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
        TaskNames.append(row[0])
        Types.append(row[2])
    fr.close()
    print("Test data sheet is running")
    timestr=time.strftime("%d-%m-%Y--%H:%M:%S")
    resultsFileName='ML_Results '+timestr+'.csv'
    fp=open(resultsFileName,'w')
    fp.write(",".join(['Expected Task Name','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','Kore Total CS score','Kore ML score','Matched Intent(s) API','Status','ScoreApi','Matched Intent(s) Luis','Status,ScoresLuis']) + '\n')
    for i in tqdm(range(len(Utterances))):
        output=[]
        output.append(TaskNames[i])#'''In the output, appending the inputs and matched intents to compare with the expected task name'''
        output.append(Utterances[i])
        output.append(Types[i])
        MatchedIntents_qabots=callKoreBot(token_QAbots, Utterances[i])    
        MatchedIntents_Api=callAPIBot(Utterances[i])    
        MatchedIntents_Luis=callLUISBot(Utterances[i])
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
    for i in outputs:
        fp.write(','.join(i) + '\n')#'''Printing the output results'''
    fp.close()
    return resultsFileName
def callKoreBot(token_QAbots, input_data):
        try:
                resp=requests.post(urlKa+\
                      uid_QAbots+urlKb\
                       +streamid_QAbots+urlKc,\
                            headers={'authorization':token_QAbots},\
                    data={ "input":input_data,"streamName":botname_QAbots})#'''Hitting find intent API call for kore.ai'''
        except:
                print(resp.text)

        url = urlKa+uid_QAbots+urlKb+streamid_QAbots+"/getTrainLogs"
        querystring = {"rnd":"6ye6to"}
        payload = "{\"input\":\""+input_data+"&#160;\",\"streamName\":\""+botname_QAbots+"\"}"
        headers = {
    'authorization': token_QAbots,
    'content-type': "application/json;charset=UTF-8",
            }
        try:
                response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        except:
                print(response.text)

        if not resp.json()=={} and resp.json().has_key('intent') and not resp.json()['intent'] ==[] and not resp.json()['intent']==None and resp.json()['intent'][0].has_key('name'):
            MatchedIntents_qabots=resp.json()['intent'][0]['name']
            if(response.json()['response']['intentMatch']==[]):
                koreCSScore='Null'
                koreMLScore='Null'
            else:
                try:
                    koreCSScore=response.json()['response']['intentMatch'][0]['totalScore']
                except:
                    koreCSScore='Null'
                try:
                    koreMLScore=response.json()['response']['intentMatch'][0]['mlScore']              
                except:    
                    koreMLScore='Null'              

        else:
            MatchedIntents_qabots='Empty Response qabots'
            koreCSScore='Null'
            koreMLScore='Null'
        if(MatchedIntents_qabots=='Default Fallback Intent'):
                MatchedIntents_qabots='None'
        koreArray=[MatchedIntents_qabots,koreCSScore,koreMLScore]
        return koreArray                

def callAPIBot(input_data):
    payload = {"q":input_data,"lang":"en","sessionId":botname_API}
    payload=str(payload)
    headers = {
        'authorization': "Bearer "+Token_Api,
        'content-type': "application/json",
         }
    try:
        response = requests.request("post", url, data=payload, headers=headers)#'''Hitting the API call for api.ai'''
    except:
        print(response.text)

    if not response.json()=={} and response.json().has_key('result') and response.json()['result'].has_key('metadata') and response.json()['result']['metadata'].has_key('intentName'):
            MatchedIntents_Api=response.json()['result']['metadata']['intentName']
            score=response.json()['result']['score']
    else:
            MatchedIntents_Api='Empty Response api'
            score=['null']
    
    if(MatchedIntents_Api=='Default Fallback Intent'):
            MatchedIntents_Api='None'        
    
    ApiArray=[MatchedIntents_Api,score]
    return ApiArray
            
def callLUISBot(input_data):
        try:
                respLuis=requests.get(urlL+input_data)#'''Reading the JSON response for luis.ai'''
        except:
                print(respLuis.text)

        respluis=respLuis.json()
        if respluis!={} and respluis.has_key('topScoringIntent') and respluis['topScoringIntent'].has_key('intent') and respluis['topScoringIntent']['intent']!='None':
                MatchedIntents_Luis=respluis['topScoringIntent']['intent']#Luis Output Taken Here
                score=respluis['topScoringIntent']['score']
        else:         
                MatchedIntents_Luis='Empty Response'
                score='Null'

        luisArray=[MatchedIntents_Luis,score]        
        return luisArray

def anothermain():
    start_time=time.time()
    resultsFileName=main()
    print(time.time()-start_time)
    tabulate.main(resultsFileName)


if __name__ == "__main__":
    anothermain()


