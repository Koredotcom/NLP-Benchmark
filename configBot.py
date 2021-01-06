import json


with open("configBot.json", "r") as fp:
	conf = json.load(fp)

fileName =  conf["fileName"]  #conf["ML_Train.csv"]
TestFileName =  conf["TestFileName"]  #"ML_TestData.csv"
RESULTSFILE =  conf["RESULTSFILE"]  #""
debug =  conf.get("debug")  #True
botName =  conf["botName"]  #"BankBot"
lang =  conf["lang"]  #"en"
threshold =  conf["threshold"]  #"en"

# Platforms to enable
USEKORE =  conf["USEKORE"]  #True
USEGOOGLE =  conf["USEGOOGLE"]  #False
USELUIS =  conf["USELUIS"]  #False
USEWATSON =  conf["USEWATSON"]  #False
USEWIT =  conf["USEWIT"]  #False

# Kore.ai
KorePlatform =  conf["KorePlatform"]  #"https://bots.kore.ai"
ssoKore = conf["ssoKore"]
userIdKore = conf["userIdKore"] 
authTokenKore = conf["authTokenKore"] 
KoreEmailId = conf["KoreEmailId"]  #
KorePassword = conf["KorePassword"]  #
jwtToken = conf.get("jwtToken", None)
koreClientId  = conf.get("koreClientId")
koreClientName = conf.get("koreClientName")
koreClientSecret = conf.get("koreClientSecret")
# optional platforms to enable to compare with kore
# Luis.ai
subscriptionToken= conf.get("subscriptionToken")  #

# DialogFlow.ai
Token_DF =  conf.get("Token_DF")
botIdDF =  conf.get("botIdDF")
Client_DF = conf.get("DF_CLIENT_ACCESS_TOKEN")
# Watson.ai
watson_uid =  conf.get("watson_uid")
watson_passwd =  conf.get("watson_passwd")

# Wit.ai
witUserToken =  conf.get("witUserToken")

