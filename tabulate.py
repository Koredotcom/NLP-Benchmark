import sys
from odfhandle import *
from watson import *
TyOfUtt=[]#Reading the type of utterances from input ML_Result csv file
success=[[],[],[],[]]
intent=[]
matched=[[],[],[],[]]
precession=[0,0,0,0]
recall=[0,0,0,0]
fscore=[0,0,0,0]
accuracy=[0,0,0,0]

def process_ambiguity(r):
	r = [cell.value for cell in r]
	if "ambiguity:" in r[3].lower():
		r[3] = "None"
	return  r

def main(ods):
	sheets=[sheet for sheet in ods.sheets][1:]
	for sheet in sheets: del sheet
	rows=[process_ambiguity(r) for r in ods.sheets[0].rows()][1:]

	for x in rows:
		if not x[0]:continue
		intent.append(WatsonCleanIntent(x[0]))
		TyOfUtt.append(x[2])
		matched[0].append(WatsonCleanIntent(x[ 3]))
		matched[1].append(WatsonCleanIntent(x[ 8]))
		matched[2].append(WatsonCleanIntent(x[11]))
		matched[3].append(WatsonCleanIntent(x[14]))
		success[0].append(x[4])
		success[1].append(x[9])
		success[2].append(x[12])
		success[3].append(x[15])
	numIntents=len(set(intent))+1
	numrows=numIntents*16
	colsMax=11
	if len(ods.sheets) <2:ods.sheets += Sheet()
	if len(ods.sheets) <3:ods.sheets += Sheet()
	sheetAll=ods.sheets[1]
	sheetAll.name="Summary"
	sheetAll._cellmatrix.reset((22+10,colsMax+10))
	sheetInd=ods.sheets[2]
	sheetInd.name="Individual Intents"
	sheetInd._cellmatrix.reset((numrows+10,colsMax+10))
	RowNum[0]=0
	for ints in sorted(set(intent)):
		if ints != "None":
			writeCSV(sheetInd,ints)

	writeCSV(sheetInd,"None")
	writeCSV((sheetAll,sheetInd), None)
	ods.save()

def writeCSV(sheet,currentIntent=None):
	if not currentIntent:
		sheetInd=sheet[1]
		sheet=sheet[0]
		name=sheetInd.name
		b1=["","KORE.AI: ALL","KORE.AI: NONE","","API.AI:ALL","API.AI:NONE","","LUIS.AI:ALL","LUIS.AI:NONE","","Watson:ALL","Watson:None",""]
	else:
		name=sheet
		b1=["","KORE.AI","","API.AI","","LUIS.AI","","Watson",""]
	b2=["TP"]
	b3=["TN"]
	b4=["FN"]
	b5=["FP"]
	c1=["","KORE.AI","","API.AI","","LUIS.AI","","Watson"]
	c2=["Precision"]
	c3=["Recall"]
	c4=["F Measure"]
	c5=["Accuracy"]

	arrayD=["Type Of Utterance","Success_Kore.ai","Failure_Kore.ai","Success_Api.ai","Failure_Api.ai","Success_Luis.ai","Failure_Luis.ai","Success_Watson","Failure_Watson","Total Utterances"]
	array1=["Positive"]
	array2=["Negative"]
	array3=["Structurally different"]
	array4=["Stemming and Lemmatization"]
	array5=["Spell Error"]
	"""Loop for the three platforms for result table calculation"""
	for platforms in range(4):
		totalPositives=0
		truePositives=0
		falseNegatives=0
		totalNegatives=0
		trueNegatives=0
		falsePositives=0
		truePositivesNone=0
		falsePositivesNone=0
		trueNegativesNone=0
		falseNegativesNone=0
		totalStruct=0
		strucTruePositive=0
		strucFalseNegative=0
		totalStem=0
		stemTruePositive=0
		stemFalseNeg=0
		spellTruePos=0
		spellFalseNeg=0
		totalSpell=0
		intentset = set(intent)
		lenintent = len(intentset)
		if currentIntent:
			lenintent = 1
			intentset = set([currentIntent])
		for currentintent in intentset:
			for i in range(len(TyOfUtt)):
				if(currentintent==matched[platforms][i] and intent[i]==matched[platforms][i]):
					if currentintent =="None":
						truePositivesNone +=1
					else:
						truePositives +=1
				if(currentintent==matched[platforms][i] and intent[i]!=matched[platforms][i]):
					if currentintent == "None":
						falsePositivesNone +=1
					else:
						falsePositives +=1
				if(currentintent!=matched[platforms][i] and currentintent != intent[i] and matched[platforms][i]==intent[i]):
					if currentintent == "None":
						trueNegativesNone +=1
					else:
						trueNegatives +=1
				if(currentintent!=matched[platforms][i] and currentintent == intent[i]):
					if currentintent == "None":
						falseNegativesNone +=1
					else:
						falseNegatives += 1
				if(TyOfUtt[i].lower()=="structurally different"):
					if(success[platforms][i]=="pass"):
						if(currentintent == None or currentintent==intent[i]):
							strucTruePositive+=1
					elif(success[platforms][i]=="fail"):
						if(currentintent == None or currentintent==intent[i]):
							strucFalseNegative+=1
					totalStruct=strucTruePositive+strucFalseNegative
				elif(TyOfUtt[i].lower()=="stemming and lemmatization"):
					if(success[platforms][i]=="pass"):
						if(currentintent == None or currentintent==intent[i]):
							stemTruePositive+=1
					elif(success[platforms][i]=="fail"):
						if(currentintent == None or currentintent==intent[i]):
							stemFalseNeg+=1
					totalStem=stemTruePositive+stemFalseNeg
				elif(TyOfUtt[i].lower()=="spell errors"):
					if(success[platforms][i]=="pass"):
						if(currentintent == None or currentintent==intent[i]):
							spellTruePos+=1
					elif(success[platforms][i]=="fail"):
						if(currentintent == None or currentintent==intent[i]):
							spellFalseNeg+=1
					totalSpell=spellTruePos+spellFalseNeg
		totalPositives=truePositives+falseNegatives+truePositivesNone+falseNegativesNone
		totalNegatives=trueNegatives+falsePositives+trueNegativesNone+falsePositivesNone
		array1.append(truePositives+truePositivesNone)
		array1.append(falseNegatives+falseNegativesNone)
		array2.append(trueNegatives)
		array2.append(falsePositives)
		array3.append(strucTruePositive)
		array3.append(strucFalseNegative)
		array4.append(stemTruePositive)
		array4.append(stemFalseNeg)
		array5.append(spellTruePos)
		array5.append(spellFalseNeg)
		try:
			arrayB=[b1,b2,b3,b4,b5]
			arrayC=[c1,c2,c3,c4,c5]
			#calculateAndInsert( totalPositives, truePositives+truePositivesNone, falseNegatives+falseNegativesNone, totalNegatives, trueNegatives+trueNegativesNone, falsePositives+falsePositivesNone, currentintent, platforms)

			if currentIntent:
				(prec,rec,acc,F) = formula(RowNum[0],colNum(len(arrayB[1])),lenintent,name)
			else:
				(prec,rec,acc,F) = formula(RowNum[0],colNum(len(arrayB[1])),lenintent,name)
			if currentIntent !="None":
				arrayB[1].append(truePositives)
			if not currentIntent or currentIntent =="None":
				arrayB[1].append(truePositivesNone)
			arrayB[1].append("")
			if currentIntent !="None":
				arrayB[2].append(trueNegatives)
			if not currentIntent or currentIntent =="None":
				arrayB[2].append(trueNegativesNone)
			arrayB[2].append("")
			if currentIntent !="None":
				arrayB[3].append(falseNegatives)
			if not currentIntent or currentIntent =="None":
				arrayB[3].append(falseNegativesNone)
			arrayB[3].append("")
			if currentIntent !="None":
				arrayB[4].append(falsePositives)
			if not currentIntent or currentIntent =="None":
				arrayB[4].append(falsePositivesNone)
			arrayB[4].append("")
			if currentIntent or True:
				arrayC[1].append(prec)
				arrayC[1].append("")
				arrayC[2].append(rec)
				arrayC[2].append("")
				arrayC[3].append(F)
				arrayC[3].append("")
				arrayC[4].append(acc)
				arrayC[4].append("")
		except Exception as e:
			print(e)
			continue
	array1.append(totalPositives)
	array2.append(totalNegatives)
	array3.append(totalStruct)
	array4.append(totalStem)
	array5.append(totalSpell)
	array=[arrayD,array1,array2,array3,array4,array5]
	"""printing the three result tables for all the three platforms"""
	if currentIntent:
		insertRow(sheet,[currentIntent])
	else:
		insertRow(sheetInd,["ALL"])
	for i in range(len(arrayB)):
		row=[]
		for j in range(len(arrayB[i])):
			row.append(arrayB[i][j])
		if currentIntent:
			insertRow(sheet,row)
		else:
			insertRow(sheetInd,row)
	if currentIntent:
		insertRow(sheet,[])
	else:
		insertRow(sheetInd,[])
	if not currentIntent:
		RowNum[0]=0
	for i in range(len(arrayC)):
		row=[]
		for j in range(len(arrayC[i])):
			row.append(arrayC[i][j])
		insertRow(sheet,row,currentIntent)
	insertRow(sheet,[],currentIntent)
	insertFormula(lenintent)


if __name__=="__main__":
		resultsFileName = sys.argv[1]
		try:
			ods = opendoc(filename=resultsFileName)
			ods.sheets[0]
		except Exception as e:
			print("File not found")
		main(ods)

