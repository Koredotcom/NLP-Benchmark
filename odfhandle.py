from ezodf import newdoc, opendoc, Sheet

RowNum = [0] #row number to replace row
def colNum(colNo):
	return chr(colNo+65)

def replaceRow(sheet, row, index, visibility=None):
	if visibility:
		sheet.row_info(index).visibility=u"collapse"
	cells=sheet.row(index)
	if not row:
		row=[]
	for cell,val in zip(cells,row):
		if type(val)==type("") and len(val)>0 and val[0]=="=":
			cell.formula=val
		else:
			cell.set_value(val)

def insertRow(sheet,row,visibility=None):
	replaceRow(sheet, row, RowNum[0], visibility)
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
	prec="=IFERROR("
	rec="=IFERROR("
	acc="=IFERROR("
	F="=IFERROR("
	row=row+3
	if type(name)==type(""):name = "'"+name+"'."
	else:name=""
	tp=name+col+str(row)
	tn=name+col+str(row+1)
	fn=name+col+str(row+2)
	fp=name+col+str(row+3)
	prec+= tp+" / ( "+tp+" + "+fp+" ) , 0 )"
	rec+= tp+"/("+tp+"+"+fn+"), 0)"
	acc+="("+tp+"+"+tn+")/("+tp+"+"+fn+"+"+tn+"+"+fp+"), 0)"
	F+="("+"2*"+tp+")/(2*"+tp+"+"+fp+"+"+fn+"), 0)"
	return (prec,rec,acc,F)

