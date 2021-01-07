#!/bin/env python
import os,sys,time,io,re,requests,json
from constants import dataset_mapping
from dfConfig import *
if sys.version[0]==2:
	print("Use python3")
	exit(1)

userIdKore=""
authTokenKore=""
KoreEmailId=""
KorePassword=""
witUserToken = ""
watson_uid = ""
watson_passwd = ""
ssoKore = ""
KorePlatform = ""
dataset=""

existing_dataset = input("Do you want to evaluate on existing Benchmark datasets(y/n)")
existing_dataset = existing_dataset or 'n'
if existing_dataset in ['y', 'Y']:
	dataset = input("Choose the dataset (1/2/3/4)\n1 NLU-AskUbuntu\n2 NLU-Webapp\n3 NLU-Chatbot\n4 Banking77\n")

while dataset not in ["1", "2", "3", "4"]:
	dataset = input("Please type valid number(1/2/3/4)\n1 NLU-AskUbuntu\n2 NLU-Webapp\n3 NLU-Chatbot\n4 Banking77\n")

dataset = int(dataset)
# USELUIS=input("Use Luis?(y/n):").lower().strip()
# USELUIS = USELUIS or 'n'
# while USELUIS not in ["y","n"]: USELUIS=input("please enter y/n only:").lower().strip()

subscriptionToken=""
Token_DF=""
botIdDF=""
# if USELUIS == "y":
# 	USELUIS=True
# 	subscriptionToken=input("Please give your luis.ai subscription token:").strip()
# else: USELUIS=False
USELUIS=False

USEDF=input("Use Dialog Flow?(y/n)").lower().strip()
USEDF = USEDF or 'n'
while USEDF not in ["y","n"]: USEDF=input("please enter y/n only:").lower().strip()
Client_DF = ""
botIdDF = ""
Token_DF = ""
if USEDF in ["Y","y"]:
	USEDF=True
	dfPrerequistes = input("Have you provided neccessary details in dfConfig.json [y/n)")
	dfPrerequistes = dfPrerequistes or 'n'
	if dfPrerequistes == 'n':
		print("Skipping evaluation on Dialog flow as prerequiste config is not provided")
		USEDF = False
	# Token_DF=input("Please give your dialogflow.ai developer token:").strip()
	# Client_DF=input("Please give your dialogflow.ai client access token:").strip()
	# botIdDF=input("Please give the id of the bot in dialogflow.ai you want to use:").strip()
else: USEDF=False

USEKORE=input("Use Kore?(y/n)").lower().strip()
USEKORE = USEKORE or 'y'
# if not USEKORE: USEKORE = 'y'
# while USEKORE not in ["y","n"]: USEKORE=input("please enter y/n only:").lower().strip()
# USEKORE = 'y'
if USEKORE == "y":
	USEKORE=True
	KorePlatform=input("Please give the kore.ai environment you want to use(default:https://bots.kore.ai):").lower().strip()
	if not KorePlatform:KorePlatform="http://localhost"

	#If running with company account id, please mark ssoKore as 'True' and enter the user-Id along with Authorization bearer in the command prompt. Else, enter you login credentials in the terminal.

	ssoKore=input("How do you want to login to kore.ai?(bearer/password):").lower().strip()
	ssoKore = ssoKore or 'password'
	while ssoKore not in ["bearer","password"]:
		ssoKore=input("please enter bearer/password only:").lower().strip()
		userIdKore=""
		authTokenKore=""
		KoreEmailId=""
		KorePassword=""
	if ssoKore == "bearer":
		ssoKore=True
		userIdKore=input('Enter userId for kore: ')
		authTokenKore=input('Enter authorization token for kore: ')
	else:
		ssoKore=False
		KoreEmailId=input('Enter kore Email Id: ')#login credentials for kore
		KoreEmailId = KoreEmailId
		KorePassword=input('Enter kore Password: ')
		KorePassword = KorePassword
	koreClientId=None # input("koreClientId:")
	koreClientName=None # input("koreClientName:")
	koreClientSecret=None # input("koreClientSecret:")
else:
	USEKORE=False

# USEWATSON = input("Use Watson?(y/n)").lower().strip()
# USEWATSON = USEWATSON or 'n'
# while USEWATSON not in ["y","n"]: USEWATSON=input("please enter y/n only:").lower().strip()
# if USEWATSON == "y":
# 	USEWATSON=True
# 	watson_uid = input("please enter watson user Id:")
# 	watson_passwd = input("please enter watson password:")
# else:
# 	USEWATSON=False
# 	watson_uid = ""
# 	watson_passwd = ""

USEWATSON=False
watson_uid = ""
watson_passwd = ""

fileDir = os.path.dirname(os.path.realpath('__file__'))
if existing_dataset in ['y', 'Y']:
	evaluation_dataset = dataset_mapping[dataset-1]
	trainFilePath = "datasets/{}/train.csv".format(evaluation_dataset)
	fileName = os.path.join(fileDir, trainFilePath)
	testFilePath = "datasets/{}/test.csv".format(evaluation_dataset)
	TestFileName = os.path.join(fileDir, testFilePath)
else:
	fileName = input("Training file name?[default is \"ML_Train.csv\"] ").strip()
	TestFileName = input("Training file name?[default is \"ML_TestData.csv\"] ").strip()
	fileName="ML_Train.csv" if fileName == "" else fileName
	TestFileName = "ML_TestData.csv" if TestFileName == "" else TestFileName

botName = input("Please enter name of the bot you want to create(default:BankBot):")
botName = botName
if not botName:botName = "BankBot"

def getThreshold(default=0.3):
	threshold = input("Minimum confidence for intent must be between 0 and 1 (default: {}):".format(default))
	if threshold.strip() == "":
		threshold = 0.3
	fail = 0
	try:
		threshold = float(threshold)
	except:
		fail = 1
	if abs(1 - threshold) > 1:
		fail = 1
	if fail == 1:
		return getThreshold(default)
	return threshold 

threshold = getThreshold()

conf ={
	"fileName":fileName,
	"TestFileName":TestFileName,
	"ssoKore":ssoKore,
	"KorePlatform":KorePlatform,
	"USEKORE":USEKORE,
	"USEGOOGLE":USEDF,
	"USEWATSON":USEWATSON,
	"USELUIS":USELUIS,
	"USEWIT":False,        # ?? why       
	"subscriptionToken":subscriptionToken,
	"Token_DF":Token_DF,
	"botIdDF":botIdDF,
	"DF_CLIENT_ACCESS_TOKEN":Client_DF,
	"userIdKore":userIdKore,
	"authTokenKore":authTokenKore,
	"KoreEmailId":KoreEmailId,
	"KorePassword":KorePassword,
	"witUserToken":witUserToken,
	"watson_uid":watson_uid,
	"watson_passwd":watson_passwd,
	"botName":botName,
	"threshold":threshold,
	"RESULTSFILE":"",
	"lang":"en"
}

with open("configBot.json", "w") as fp:
	json.dump(conf, fp, indent=4)
