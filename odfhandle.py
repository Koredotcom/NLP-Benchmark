from ezodf import newdoc, opendoc, Sheet

RowNum = [0] #row number to replace row
def colNum(colNo):
	return chr(colNo+65)

def insertRow(sheet,row,visibility=None):
	if visibility:
		sheet.row_info(RowNum[0]).visibility=u"collapse"
	cells=sheet.row(RowNum[0])
	if not row:
		row=[]
	for cell,val in zip(cells,row):
		if len(val)>0 and val[0]=="=":
			cell.formula=val
		else:
			cell.set_value(val)
	RowNum[0] =RowNum[0]+ 1

def insertFormula(lenintents):
	prec=RowNum[0]-5
	recall=prec+1
	F=prec+2
	acc=prec+3
	#sheet[prec,1].formula=0

def next_set(i,col):
	return (col+str(13*i+9),col+str(13*i+10),col+str(13*i+11),col+str(13*i+12))

def formula(row,col,lenintent,name):
	prec="=("
	rec="=("
	acc="=("
	F="=("
	if lenintent == 1:
		prec="=IFERROR("
		rec="=IFERROR("
		acc="=IFERROR("
		F="=IFERROR("
		row=row+3
		tp=col+str(row)
		tn=col+str(row+1)
		fn=col+str(row+2)
		fp=col+str(row+3)
		prec+= tp+"/("+tp+"+"+fp+"), 0)"
		rec+= tp+"/("+tp+"+"+fn+"), 0)"
		acc+="("+tp+"+"+tn+")/("+tp+"+"+fn+"+"+tn+"+"+fp+"), 0)"
		F+="("+"2*"+tp+")/(2*"+tp+"+"+fp+"+"+fn+"), 0)"
	else:
		for i in range(lenintent):
			n=next_set(i,col)
			prec+="'"+name+"'."+n[0]+"+"
			rec+="'"+name+"'."+n[1]+"+"
			F+="+'"+name+"'."+n[2]+"+"
			acc+="'"+name+"'."+n[3]+"+"
		prec+="0.0)/"+str(lenintent)
		rec+="0.0)/"+str(lenintent)
		F+="0.0)/"+str(lenintent)
		acc+="0.0)/"+str(lenintent)
	return (prec,rec,acc,F)

