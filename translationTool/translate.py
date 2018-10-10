from googleapiclient.discovery import build


from tqdm import tqdm
import time
class googleTranslate:
	def __init__(self,src="en",dest="fr"):
		self.Translator = build('translate', 'v2',
            developerKey='use your api key')
		self.src    = src
		self.dest   = dest
		self.count  =0 

	def translateSentence(self,sentence):
		Translator=self.Translator
		translatedText = None
		try:
			translatedText = self.Translator.translations().list(
														source=self.src,
														target=self.dest,
														q=sentence
														).execute()
			return translatedText["translations"][0]["translatedText"]
		except Exception as e:
			print(sentence)
			print(translatedText)
			print(e)
			print("error in google translate")
			time.sleep(10)
			return self.translateSentence(sentence,)

		return sentence

	def listofValues(self,lookuplist):
		for obj in lookuplist:
			if type(obj["synonyms"]) is str:
				obj["synonyms"] = self.translateSentence(obj["synonyms"] )
			else:
				for idx,val in enumerate(obj["synonyms"]):
					lis = []
					for syn in val.split(","):
						if len(syn)>0  and syn[0] =='"' and syn[-1] == '"':
							lis.append('"'+self.translateSentence(syn[1:-1])+'"')
						else:
							lis.append(self.translateSentence(syn))
					obj["synonyms"][idx] = ",".join(x for x in lis)
		return
		
	def FAQS(self,faqPayload):
		if "faqs" in faqPayload:
			faqs = faqPayload["faqs"]
			print("Translating FAQS:\n")
			for faq in tqdm(faqs):
				faq["question"]=self.translateSentence(faq["question"])
				for j in range(0,len(faq["alternateQuestions"])):
					faq["alternateQuestions"][j]["question"]=self.translateSentence(faq["alternateQuestions"][j]["question"])

	def MlSentences(self,sentences):
		print("Translating ML Sentences:\n ")
		for sentence in tqdm(sentences):
			sentence["sentence"]=self.translateSentence(sentence["sentence"])
			if "entities" in sentence:
				del sentence["entities"]

	def Dialogs(self,components,dest,src):
		for  idx,dialog in enumerate(components):
			components[idx]["localeData"][src]["name"] = self.translateSentence(dialog["localeData"][src]["name"]) 
			components[idx]["lname"] = self.translateSentence(dialog["lname"])

	def DialogComponents(self,components,dest,src):
		print("Translating DialogComponents:\n")
		for component in tqdm(components):
			if "type" in component and component["type"]=="intent":
				component["name"] = component["localeData"][src]["intent"]=self.translateSentence(component["localeData"][src]["intent"])
			elif component["type"] =="entity" and component["entityType"] =="list_of_items_lookup":
					self.listofValues(component["lookupValues"])
			elif component["type"] =="entity" and component["entityType"] =="list_of_values":
				if "values" in component["localeData"][src]["allowedValues"]:
					self.listofValues(component["localeData"][src]["allowedValues"]["values"])

	def BotDefinition(self,payload,dest,src):
		if "dialogs" in payload:
			self.Dialogs(payload["dialogs"],dest,src)
		if "dialogComponents" in payload:
			self.DialogComponents(payload["dialogComponents"],dest,src)
		if "sentences" in payload:
			self.MlSentences(payload["sentences"])
		if "knowledgeTasks" in payload:
			if len(payload["knowledgeTasks"])==1:
				self.FAQS(payload["knowledgeTasks"][0]["faqs"])

	def AutomationSuite(self,payload):
		if "testCases" in payload:
			testCases = payload["testCases"]
			for idx,testcase in enumerate(testCases):
				messages=testcase["messages"]
				for idx2,message in enumerate(messages):
					testCases[idx]["messages"][idx2]["input"]=self.translateSentence(message["input"])

	def BatchTestSuite(self,payload):
		if "testCases" in payload:
			testCases = payload["testCases"]
			for testcase in tqdm(testCases):
				testcase["input"]=self.translateSentence(testcase["input"])
				testcase["intent"]=self.translateSentence(testcase["intent"])
	
	def localeCodes(self,errorCodes):
		for errorCode in tqdm(errorCodes):
			errorCodes[errorCode]=self.translateSentence(errorCodes[errorCode])

	def koraGenericResponses(self,payload):
		genericKoraResponses = payload["koraGenericResponses"]
		for koraresponse in tqdm(genericKoraResponses):
			koraresponse["Original Message"]=self.translateSentence(koraresponse["Original Message"])

	def defaultErrorCodeScript(self,payload):
		pollErrors=payload["errorCodes"]["pollErrors"]
		for pollerror in tqdm(pollErrors):
			error=pollErrors[pollerror]
			error["message"]=self.translateSentence(error["message"])
			if "errorMessages" in error:
				if "poll" in error["errorMessages"]:
					error["errorMessages"]["poll"]["title"]=self.translateSentence(error["errorMessages"]["poll"]["title"])
					error["errorMessages"]["poll"]["body"]=self.translateSentence(error["errorMessages"]["poll"]["body"])
				if "fetch" in error["errorMessages"]:
					error["errorMessages"]["fetch"]["title"]=self.translateSentence(error["errorMessages"]["fetch"]["title"])
					error["errorMessages"]["fetch"]["body"]=self.translateSentence(error["errorMessages"]["fetch"]["body"])
				if "action" in error["errorMessages"]:
					error["errorMessages"]["action"]["title"]=self.translateSentence(error["errorMessages"]["action"]["title"])
					error["errorMessages"]["action"]["body"]=self.translateSentence(error["errorMessages"]["action"]["body"])