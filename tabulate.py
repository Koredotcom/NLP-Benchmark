from __future__ import print_function
import requests, csv, os, time,sys
TyOfUtt=[]#'''Reading the type of utterances from input ML_Result csv file'''
success1=[]
success2=[]
success3=[]
b1=['','','KORE.AI','','API.AI','','LUIS.AI']
b2=['TP']#'''Global arrays declared for true positives table'''
b3=['TN']
b4=['FN']
b5=['FP']
c1=['','KORE.AI','','API.AI','','LUIS.AI']
c2=['Precision']#'''Global arrays declared for formulae calculation table'''
c3=['Recall']
c4=['F Measure']
c5=['Error']
c6=['Accuracy']

def main():
	fr=open('ML_Results.csv','r')
	try:
		reader=csv.reader(fr,delimiter=',')
		x = reader.next()
		while 1:
			try:
				x = reader.next()
				TyOfUtt.append(x[2])
				success1.append(x[4])
				success2.append(x[8])
				success3.append(x[11])
			except StopIteration:
				break

		fr.close()
	except:
		print("File not found")
        timestr=time.strftime("%d-%m-%Y--%H:%M:%S")	
	fr1=open('Summary '+timestr+'.csv','w')
	success=[success1,success2,success3]
	platforms=0
	totalPositives=0
	truePositives=0
	falseNegatives=0
	totalNegatives=0
	trueNegatives=0
	falsePositives=0
	totalStruct=0
	strucTruePositive=0
	strucFalseNegative=0
	totalStem=0
	stemTruePositive=0
	stemFalseNeg=0
	spellTruePos=0
	spellFalseNeg=0
	totalSpell=0		
	arrayD=['Type Of Utterance','Success_Kore.ai','Failure_Kore.ai','Success_Api.ai','Failure_Api.ai','Success_Luis.ai','Failure_Luis.ai','Total Utterances']
	array1=[]
	array1.append('Positive')
	array2=[]
	array2.append('Negative')
	array3=[]
	array3.append('Structurally different')
	array4=[]
	array4.append('Stemming and Lemmatization')
	array5=[]
	array5.append('Spell Error')
	'''Loop for the three platforms for result table calculation'''
	while platforms<3:
		totalPositives=0
		truePositives=0
		falseNegatives=0
		totalNegatives=0
		trueNegatives=0
		falsePositives=0
		totalStruct=0
		strucTruePositive=0
		strucFalseNegative=0
		totalStem=0
		stemTruePositive=0
		stemFalseNeg=0
		spellTruePos=0
		spellFalseNeg=0
		totalSpell=0		
        
		for i in range(len(TyOfUtt)):
			if(TyOfUtt[i]=='Positive'):
				if(success[platforms][i]=='pass'):
					truePositives+=1
				elif(success[platforms][i]=='fail'):
					falseNegatives+=1
				totalPositives=truePositives+falseNegatives
			elif(TyOfUtt[i]=='Negative'):
				if(success[platforms][i]=='pass'):
					trueNegatives+=1
				elif(success[platforms][i]=='fail'):
					falsePositives+=1
				totalNegatives=trueNegatives+falsePositives
			elif(TyOfUtt[i]=='Structurally Different'):
				if(success[platforms][i]=='pass'):
					strucTruePositive+=1
				elif(success[platforms][i]=='fail'):
					strucFalseNegative+=1
				totalStruct=strucTruePositive+strucFalseNegative
			elif(TyOfUtt[i]=='Stemming and Lemmatization'):
				if(success[platforms][i]=='pass'):
					stemTruePositive+=1
				elif(success[platforms][i]=='fail'):
					stemFalseNeg+=1
				totalStem=stemTruePositive+stemFalseNeg
			elif(TyOfUtt[i]=='Spell Errors'):
				if(success[platforms][i]=='pass'):
					spellTruePos+=1
				elif(success[platforms][i]=='fail'):
					spellFalseNeg+=1
				totalSpell=spellTruePos+spellFalseNeg
		#array1.append(q)
		array1.append(truePositives)
		array1.append(falseNegatives)
		array2.append(trueNegatives)
		array2.append(falsePositives)
		array3.append(strucTruePositive)
		array3.append(strucFalseNegative)
		array4.append(stemTruePositive)
		array4.append(stemFalseNeg)
		array5.append(spellTruePos)
		array5.append(spellFalseNeg)		
		if(platforms==0):		
			calculateAndInsert(totalPositives, truePositives, falseNegatives, totalNegatives, trueNegatives, falsePositives, totalStruct, strucTruePositive, strucFalseNegative, totalStem, stemTruePositive, stemFalseNeg, spellTruePos, spellFalseNeg, totalSpell)#'''Calling the function for formulae calculation and result tables i.e. to identify the sum of false positives, false negatives, etc'''
		elif(platforms==1):
			calculateAndInsert(totalPositives, truePositives, falseNegatives, totalNegatives, trueNegatives, falsePositives, totalStruct, strucTruePositive, strucFalseNegative, totalStem, stemTruePositive, stemFalseNeg, spellTruePos, spellFalseNeg, totalSpell)
		else:
			calculateAndInsert(totalPositives, truePositives, falseNegatives, totalNegatives, trueNegatives, falsePositives, totalStruct, strucTruePositive, strucFalseNegative, totalStem, stemTruePositive, stemFalseNeg, spellTruePos, spellFalseNeg, totalSpell)							
		platforms+=1	
	array1.append(totalPositives)
	array2.append(totalNegatives)
	array3.append(totalStruct)
	array4.append(totalStem)
	array5.append(totalSpell)
	array=[arrayD,array1,array2,array3,array5]	
	arrayB=[b1,b2,b3,b4,b5]
	'''printing the three result tables for all the three platforms'''
	for i in range(len(array)):
		row=''
		for j in range(len(array1)):
			row=row+str(array[i][j])+','
		fr1.write(row+"\n")
	fr1.write("\n")
	for i in range(len(arrayB)):
		row=''
		for j in range(len(b1)):
			row=row+str(arrayB[i][j])+','
		fr1.write(row+"\n")
		
	fr1.write("\n")
	arrayC=[c1,c2,c3,c4,c5,c6]
	for i in range(len(arrayC)):
		row=''
		for j in range(len(c1)):
			row=row+str(arrayC[i][j])+','
		fr1.write(row+"\n")	
	fr1.close()

def calculateAndInsert(totalPositives, truePositives, falseNegatives, totalNegatives, trueNegatives, falsePositives, totalStruct, strucTruePositive, strucFalseNegative, totalStem, stemTruePositive, stemFalseNeg, spellTruePos, spellFalseNeg, totalSpell):
	prK=round((truePositives+strucTruePositive+spellTruePos)/float(truePositives+strucTruePositive+spellTruePos+falsePositives),4)
	rrK=round((truePositives+strucTruePositive+spellTruePos)/float(truePositives+strucTruePositive+spellTruePos+falseNegatives+strucFalseNegative+stemFalseNeg+spellFalseNeg),4)
	acK=round((truePositives+trueNegatives+strucTruePositive+spellTruePos)/float(totalPositives+totalNegatives+totalStruct+totalSpell),4)
	frK=round((2*prK*rrK)/float(prK+rrK),4)
	b2.append('')
	b2.append(truePositives+strucTruePositive+spellTruePos)
	b3.append('')
	b3.append(trueNegatives)
	b4.append('')
	b4.append(falseNegatives+strucFalseNegative+spellFalseNeg)
	b5.append('')
	b5.append(falsePositives)
	c2.append(prK)
	c2.append('')
	c3.append(rrK)
	c3.append('')
	c4.append(frK)
	c4.append('')
	c5.append('')
	c5.append('')
	c6.append(acK)
	c6.append('')


if __name__=="__main__":
	main()

