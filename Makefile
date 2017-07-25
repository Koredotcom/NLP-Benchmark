# Make file, meant for linux systems


all:
	make clean
	python createIntent.py
	echo Bots created and trained
	python read.py


clean:
	- rm ML_Results* 2>/dev/null
	- rm Summary* 2>/dev/null
	- rm *.pyc 2>/dev/null
	- rm -r __pycache__ 2>/dev/null

