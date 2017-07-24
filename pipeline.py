import os,time
x=os.system('python -m createIntent')#Calling createIntent.py
if(x==0):
        print('The bots have been trained')
        os.system('python -m read')#Calling read.py