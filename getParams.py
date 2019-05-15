#!/bin/env python
import os,sys,time,io,re,requests,json

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

USELUIS=input("Use Luis?(y/n):").lower().strip()
while USELUIS not in ["y","n"]: USELUIS=input("please enter y/n only:").lower().strip()

subscriptionToken=""
Token_DF=""
botIdDF=""
if USELUIS == "y":
	USELUIS=True
	subscriptionToken=input("Please give your luis.ai subscription token:").strip()
else: USELUIS=False

USEDF=input("Use Dialog Flow?(y/n)").lower().strip()
while USEDF not in ["y","n"]: USEDF=input("please enter y/n only:").lower().strip()

if USEDF in ["Y","y"]:
	USEDF=True
	Token_DF=input("Please give your dialogflow.ai developer token:").strip()
	botIdDF=input("Please give the id of the bot in dialogflow.ai you want to use:").strip()
else: USEDF=False


USEKORE=input("Use Kore?(y/n)").lower().strip()
while USEKORE not in ["y","n"]: USEKORE=input("please enter y/n only:").lower().strip()

if USEKORE == "y":
	USEKORE=True
	KorePlatform=input("Please give the kore.ai environment you want to use(default:https://bots.kore.ai):").lower().strip()
	if not KorePlatform:KorePlatform="https://bots.kore.ai"

	#If running with company account id, please mark ssoKore as 'True' and enter the user-Id along with Authorization bearer in the command prompt. Else, enter you login credentials in the terminal.

	ssoKore=input("How do you want to login to kore.ai?(bearer/password):").lower().strip()
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
		KorePassword=input('Enter kore Password: ')
	#koreClientId=input("koreClientId:")
	#koreClientName=input("koreClientName:")
	#koreClientSecret=input("koreClientSecret:")
else:
	USEKORE=False

USEWATSON = input("Use Watson?(y/n)").lower().strip()
while USEWATSON not in ["y","n"]: USEWATSON=input("please enter y/n only:").lower().strip()
if USEWATSON == "y":
	USEWATSON=True
	watson_uid = input("please enter watson user Id:")
	watson_passwd = input("please enter watson password:")
else:
	USEWATSON=False
	watson_uid = ""
	watson_passwd = ""

fileName = input("Training file name?[default is \"ML_Train.csv\"] ").strip()
TestFileName = input("Training file name?[default is \"ML_TestData.csv\"] ").strip()
fileName="ML_Train.csv" if fileName == "" else fileName
TestFileName = "ML_TestData.csv" if TestFileName == "" else TestFileName

botName = input("Please enter name of the bot you want to create(default:BankBot):")
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
	if abs(1 - threshold) < 1:
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
