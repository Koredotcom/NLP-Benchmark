import os,sys,time,json,requests
from configBot import WitUserToken
url = "https://api.wit.ai/"
querystring = {"verbose":"true"}
headers = {
	"accept": "application/vnd.wit.20150405+json",
	"Authorization": WitUserToken
	}

def createBot(botName, desc="", lang="en"):
	if not desc:desc=botName
	payload = [{"data":{"name":botName,"desc":desc,"lang":lang,"private":True},"type":"created-instance"}]
	response = requests.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	intentId = response.json()["instance"]["intents"][0]["id"]
	semanticTagsId = response.json()["instance"]["wisp_ids"][0]
	print("intentId",intentId)
	print("semantictagid:",semanticTagsId)
	bot = [bot for bot in response["user"]["instances"] if bot["name"] == botName][0]
	return bot["id"], bot["access_token"], intentId, semanticTagsId

def deleteBot(botId):
	payload = [{"data":{"instance_id":botId},"type":"deleted-instance"}]
	headers["x-wit-instance"]=botId
	response = requests.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def addIntentToBot(botId, semanticTagsId, intentName):
	headers["x-wit-instance"]=botId
	payload = [{"data":{"wisp":semanticTagsId,"value":intentName},"type":"added-wisp-value"}]
	response = requests.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def deleteIntentToBot(botId, intentId):
	payload = [{"data":{"wisp_id":intentId},"type":"deleted-wisp-from-instance"}]
	headers["x-wit-instance"]=botId
	response = requests.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def addUtterance(botId, intentId, semanticTagsId, utterances, intentName):
	headers["x-wit-instance"]=botId
	payload = [{"data":{"wave":None,"text":{"text":utterance},"semantic":{"intent":intentId,"entities":[{"subentities":[],"start":None,"wisp":semanticTagsId,"value":intentName,"role":None,"end":None}]}},"type":"added-semantic"} for utterance in utterances]
	response = requests.put( url+"sync", json=payload, headers=headersWit, params=querystring)
	return response

def findIntent(botToken, utterance):
	querystring = {"v":20170307,"q":utterance}
	response = requests.get( url+"message", headers={"Authorization":botToken}, params=querystring)
	return response

def test():
	if sys.argv[1] == "createBot":
		resp = createBot(sys.argv[2])
		print(resp)
		#if resp.status_code != 200:print(resp.text)
		#print([bot for bot in resp.json()["user"]["instances"] if bot["name"] == sys.argv[2]][0])
	if sys.argv[1] == "deleteBot":
		resp = deleteBot(sys.argv[2])
		print(resp.status_code, resp.json().keys(), resp.text)
	if sys.argv[1] == "addIntent":
		resp = addIntentToBot(sys.argv[2], sys.argv[3], sys.argv[4])
		print(resp.status_code, resp.json().keys(), resp.text)
	if sys.argv[1] == "deleteIntent":
		resp = deleteIntentToBot(sys.argv[2], sys.argv[3])
		print(resp.status_code, resp.json().keys(), resp.text)
	if sys.argv[1] == "addUtterance":
		resp = addUtterance(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
		print(resp.status_code, resp.text)
	if sys.argv[1] == "findIntent":
		resp = findIntent(sys.argv[2], sys.argv[3])
		print(resp.status_code, resp.text)

if __name__ == "__main__":test()


