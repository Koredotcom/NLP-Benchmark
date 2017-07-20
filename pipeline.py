import os,time
os.system('python -m createIntent')
print('Waiting for the bots to get trained')
time.sleep(45)
print('The bots have been trained')
os.system('python -m read')