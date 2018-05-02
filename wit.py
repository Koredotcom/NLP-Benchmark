import os,sys,time,json,requests
from configBot import witUserToken
url = "https://api.wit.ai/"
querystring = {"verbose":"true"}
headersWit = {
	"accept": "application/vnd.wit.20150405+json",
	"Authorization": witUserToken
	}

def createBot(session, botName, desc="", lang="en"):
	if not desc:desc=botName
	payload = [{"data":{"name":botName,"desc":desc,"lang":lang,"private":True},"type":"created-instance"}]
	response = session.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	intentId = response.json()["instance"]["intents"][0]["id"]
	semanticTagsId = response.json()["instance"]["wisp_ids"][0]
	bot = [bot for bot in response.json()["user"]["instances"] if bot["name"] == botName][0]
	return bot["id"], bot["access_token"], intentId, semanticTagsId

def deleteBot(session, botId):
	payload = [{"data":{"instance_id":botId},"type":"deleted-instance"}]
	headersWit["x-wit-instance"]=botId
	response = session.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def addIntentToBot(session, botId, semanticTagsId, intentName):
	headersWit["x-wit-instance"]=botId
	payload = [{"data":{"wisp":semanticTagsId,"value":intentName},"type":"added-wisp-value"}]
	response = session.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def deleteIntentToBot(session, botId, intentId):
	payload = [{"data":{"wisp_id":intentId},"type":"deleted-wisp-from-instance"}]
	headersWit["x-wit-instance"]=botId
	response = session.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def addUtterances(session, botId, intentId, semanticTagsId, utterances, intentName):
	headersWit["x-wit-instance"]=botId
	payload = [{"data":{"wave":None,"text":{"text":utterance},"semantic":{"intent":intentId,"entities":[{"subentities":[],"start":None,"wisp":semanticTagsId,"value":intentName,"role":None,"end":None}]}},"type":"added-semantic"} for utterance in utterances]
	response = session.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def findIntent(session, botToken, utterance):
	querystring = {"v":20170307,"q":utterance}
	response = session.get( url+"message", headers={"Authorization":botToken}, params=querystring)
	return response

def test():
	session = requests.Session()
	if sys.argv[1] == "createBot":
		resp = createBot(session, sys.argv[2])
		print(resp)
		#if resp.status_code != 200:print(resp.text)
		#print([bot for bot in resp.json()["user"]["instances"] if bot["name"] == sys.argv[2]][0])
	if sys.argv[1] == "deleteBot":
		resp = deleteBot(session, sys.argv[2])
		print(resp.status_code, resp.json().keys(), resp.text)
	if sys.argv[1] == "addIntent":
		resp = addIntentToBot(session, sys.argv[2], sys.argv[3], sys.argv[4])
		print(resp.status_code, resp.json().keys(), resp.text)
	if sys.argv[1] == "deleteIntent":
		resp = deleteIntentToBot(session,sys.argv[2], sys.argv[3])
		print(resp.status_code, resp.json().keys(), resp.text)
	if sys.argv[1] == "addUtterance":
		resp = addUtterance(session, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
		print(resp.status_code, resp.text)
	if sys.argv[1] == "findIntent":
		resp = findIntent(session, sys.argv[2], sys.argv[3])
		print(resp.status_code, resp.text)

if __name__ == "__main__":test()


