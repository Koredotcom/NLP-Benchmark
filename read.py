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
    fp=open('ML_Results.csv','w')
    fp.write(",".join(['Expected TaskName','Utterance','Type of Utterance','Matched Intent(s) Kore','Status','kore CS score','kore ML score','Matched Intent(s) API','Status','ScoreApi','Matched Intent(s) Luis','Status,ScoresLuis']) + '\n')
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
        #print(output)  
    for i in outputs:
        fp.write(','.join(i) + '\n')#'''Printing the output results'''
    fp.close()

def callKoreBot(token_QAbots, input_data):
        #print('Request Kore')
        #print(input_data)
        resp=requests.post(urlKa+\
              uid_QAbots+urlKb\
               +streamid_QAbots+urlKc,\
                   headers={'authorization':token_QAbots},\
            data={ "input":input_data,"streamName":botname_QAbots})#'''Hitting find intent API call for kore.ai'''
        url = urlKa+uid_QAbots+urlKb+streamid_QAbots+"/getTrainLogs"

        querystring = {"rnd":"6ye6to"}

        payload = "{\"input\":\""+input_data+"&#160;\",\"streamName\":\""+botname_QAbots+"\"}"
        headers = {
    'authorization': token_QAbots,
    'content-type': "application/json;charset=UTF-8",
            }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        if not resp.json()=={} and resp.json().has_key('intent') and not resp.json()['intent'] ==[] and not resp.json()['intent']==None and resp.json()['intent'][0].has_key('name'):
            MatchedIntents_qabots=resp.json()['intent'][0]['name']
            #if(MatchedIntents_qabots!='Default Fallback Intent'):
              #      koreCSScore=response.json()['response']['intentMatch'][0]['totalScore']
              #      koreMLScore=response.json()['response']['intentMatch'][0]['mlScore']              
            koreCSScore='Null'
            koreMLScore='Null'
        else:
            MatchedIntents_qabots='Empty Response qabots'
            koreCSScore='Null'
            koreMLScore='Null'

        koreArray=[MatchedIntents_qabots,koreCSScore,koreMLScore]
        return koreArray                

def callAPIBot(input_data):
    payload = {"q":input_data,"lang":"en","sessionId":botname_API}
    payload=str(payload)
    headers = {
        'authorization': "Bearer "+Token_Api,
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "e8ed767d-1b62-eb74-a97a-8036293a740d"
         }
    #print('API')
    #print(input_data)
    response = requests.request("post", url, data=payload, headers=headers)#'''Hitting the API call for api.ai'''
    if not response.json()=={} and response.json().has_key('result') and response.json()['result'].has_key('metadata') and response.json()['result']['metadata'].has_key('intentName'):
            MatchedIntents_Api=response.json()['result']['metadata']['intentName']
            score=response.json()['result']['score']
    else:
            MatchedIntents_Api='Empty Response api'
            score=['null']
    ApiArray=[MatchedIntents_Api,score]
    return ApiArray
            
def callLUISBot(input_data):
        #print('LUIS')
        #print(input_data)
        respLuis=requests.get(urlL+input_data)#'''Reading the JSON response for luis.ai'''
        respluis=respLuis.json()
        if respluis!={} and respluis.has_key('topScoringIntent') and respluis['topScoringIntent'].has_key('intent') and respluis['topScoringIntent']['intent']!='None':
                MatchedIntents_Luis=respluis['topScoringIntent']['intent']#Luis Output Taken Here
                score=respluis['topScoringIntent']['score']
        elif respluis!={} and respluis.has_key('topScoringIntent') and respluis['topScoringIntent'].has_key('intent') and respluis['topScoringIntent']['intent']=='None':
                MatchedIntents_Luis='Default Fallback Intent'
                score=respluis['topScoringIntent']['score']
        else:         
                MatchedIntents_Luis='Empty Response'
                score='Null'
        luisArray=[MatchedIntents_Luis,score]        
        return luisArray

def anothermain():
    start_time=time.time()
    main()
    print(time.time()-start_time)
    import tabulate
    tabulate.main()


if __name__ == "__main__":
    anothermain()


