#!/bin/env python
import os,sys,time,io,re,requests,json

def loginToKore(koreUserId,KorePassword,KorePlatform):
		url = KorePlatform+"/api/1.1/oauth/token"#Calling the oauth Api for Kore
		payload = "{\"client_id\":\"1\",\"client_secret\":\"1\",\"scope\":\"1\",\"grant_type\":\"password\",\"username\":\""+koreUserId+"\",\"password\":\""+KorePassword+"\"}"
		headers = {'content-type': "application/json;charset=UTF-8"}
		try:
				response = requests.post(url, data=payload, headers=headers)
		except:
				print(response.text)

		authTokenKore= "bearer "+response.json()['authorization']['accessToken']
		userIdKore=response.json()['authorization']['resourceOwnerID']
		loginResp=[authTokenKore, userIdKore]

		return loginResp

if sys.version[0]==2:
	print("Use python3")
	exit(1)

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

if USEKORE:
	KorePlatform=input("Please give the kore.ai environment you want to use(default:https://bots.kore.ai):").lower().strip()
	if not KorePlatform:KorePlatform="https://bots.kore.ai"

	#If running with company account id, please mark ssoKore as 'True' and enter the user-Id along with Authorization bearer in the command prompt. Else, enter you login credentials in the terminal.

	ssoKore=input("How do you want to login to kore.ai?(bearer/password):").lower().strip()
	while ssoKore not in ["bearer","password"]: ssoKore=input("please enter bearer/password only:").lower().strip()
	if ssoKore == "bearer":
		ssoKore=True
		userIdKore=input('Enter userId for kore: ')
		authTokenKore=input('Enter authorization token for kore: ')
	else:
		ssoKore=False
		koreUserId=input('Enter kore Email Id: ')#login credentials for kore
		KorePassword=getpass.getpass('Enter kore Password: ')
		if ssoKore is False:
			loginCred=loginToKore(koreUserId,KorePassword,KorePlatform)#Calling the login function for kore
			userIdKore=loginCred[1]
			authTokenKore=loginCred[0]

fileName="ML_Train.csv"
TestFileName = "ML_TestData.csv"

fr=open('configBot.py','w')
fr.write("fileName=	\""+fileName+"\"\n")
fr.write("TestFileName=	\""+TestFileName+"\"\n")
fr.write("ssoKore=		"+str(ssoKore)+"\n")
fr.write("KorePlatform=\""+str(KorePlatform)+"\"\n")
fr.write("USEKORE="+str(USEKORE)+"\n")
fr.write("USEGOOGLE="+str(USEDF)+"\n")
fr.write("USELUIS="+str(USELUIS)+"\n")
fr.write("subscriptionToken=	\""+subscriptionToken+"\"\n")
fr.write("Token_DF=		\""+Token_DF+"\"\n")
fr.write("botIdDF=		\""+botIdDF+"\"\n")
fr.write("userIdKore=		\""+userIdKore+"\"\n")
fr.write("authTokenKore=	\""+	authTokenKore+"\"\n")

