# INTRODUCTION

This tool helps for comparing the ML Capability in intent recognition for the platforms Kore.ai, Dialogflow (CX)

# Prerequisites
    - python dev/devel/src  >= 3.5.3 and <= 3.6.3. We suggest to use stable 3.5.3 from https://www.python.org/downloads/release/python-353/ 
        - windows installer at : https://www.python.org/downloads/windows/
    - pip 
    	- instructions from https://pip.pypa.io/en/stable/installing/ , we suggest you run this with you native python (in most Os its python2.7 linked to "python" executable)
    - virtualenv
    	- after installing pip you can simply install this by `pip install virtualenv`
        - windows instructions at https://docs.python.org/3/library/venv.html

Post installation to verify that the installations done are as expected 
	
	$ python3 --version
	Python 3.5.3          # or the version you installed
	$ pip --version
	pip 19.0.3            # or the version you installed
	$ virtualenv --version
	16.1.0                # or the version you installed

# PREPARATION OF DATA
1. There are few standard benchmark datasets available for evaluating Intent recognition capabilities of Conversational AI platforms such as Kore.AI, DialogFlow(CX). You can either choose to run on available datasets by providing the number assigned against them OR You could choose to run on your own datasets. Please follow next instruction for using own datasets.
2. Mention the Intents and the train data to be created in the ML_Train.csv file. While entering data , please follow the format as it is in ML_Train.csv
3. Mention the test data along with utterance classification ( i.e Positive/Negative/Spell Errors etc) in ML_TestData.csv. Here it is important to give the classification names properly as mentioned in the ML_TestData.csv sheet, with the necessary capitalization.

## Setup Instructions:

* Create a virtual env for this tool, if not already present ans activate it.
	```
	$ virtualenv  venv/ # if you have multiple python versions, use "virtualenv  --python=/path/to/python3 venv/"
	```
* If this is your first time running the tool, do this.
     ```
	$ pip install --upgrade pip
	$ (windows only) download twisted from https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted (appropriate version)
	$ (windows only) pip install Twisted<version>.whl
	$ pip install --upgrade -r requirements.txt
	```
* If you encounter any errors during this refer to the specific python module documentation


# Quick run
Activate the created virtual environment.
	
	$ source venv/bin/activate # (Note:- use "./venv/Scripts/activate.bat" for windows)

### Linux/MacOs 
     
	 $ ./run.sh
	 

#### Windows OR customisable use on windows and MacOs:
	 $ python getParams.py # use this to configure the run.
	 $ python createIntent.py # use this to create a new bot. To use existing bot (created by previous use), don't run this again.
	 $ python runTest.py testconfig.json # use this to obtain the test results.
	 

Do not give spaces in bot name. It is not tested with spaces, in all platforms.
Note that kore platform access token expires in finite time. so if you plan to run the testing at a later time, please update the token in testconfig.json . The testing script (runTest.py) will prompt if kore token expires during runtime.


# Help with configuring the tool

When running run.sh you will be asked for several inputs such as access tokens, URL etc

## Configuration for Kore.ai -:
* Pre-requisite for this is to ensure that you have registered and logged in into https://bots.kore.ai/botbuilder 
* Enter the name of the environment for which the Benchmark tool needs to be run.

		KorePlatform="https://bots.kore.ai"

* Enter UserId and Bearer token from any API calls recorded by the browser developer console and clicking on any bot. User Ids can be found in Request Header in request parameters and authorization token can be found under "authorization" attribute of request header. Refer samples below 

		userIdKore="u-f5047708-1b41-5dfe-960a-64fef9638329"
		authTokenKore="bearer xowAczxCrk4-bSpj3-lQNgcBmGdtIseQxFb6dyFIBZ1cheL6Vdj_1fW-e7R8MgMV"
* In configBot.py set USEKORE=True to test on kore environment else set it to False

## Configuration for DialogFlow (CX)(OPTIONAL)

### Pre-requisites
* Enable Dialogflow API in Google Cloud Project
* Create a Service account and download the service accountkey json file
* For more info, follow https://cloud.google.com/dialogflow/cx/docs/quick/setup
* Configure the downloaded service account key file path dfConfig.json SERVICE_ACCOUNT_FILE_PATH
* Provide PROJECT_ID and LOCATION_ID in dfConfig.json

#### In configBot.py set USEGOOGLE=True to test on DialogFlow environment else set it to False
#### After the required setup to use dialogflow(CX) API, fill the required details in dfConfig.json


## Configuration for Luis.ai(OPTIONAL) -:

* As soon as you login into the Luis website, press on My Keys. In this page, copy the Programmatic API key and paste it within the keys in subscriptionToken. 
* provide it when prompted - "Please give your luis.ai subscription token:"

## Configuration for IBM Watson(OPTIONAL) -:

* Create an account in Watson, and get developer name and password (different from login user name and password)
* Limitations: free account allows a maximum of 5 bots at a time. Also there is a rate limit for bot&intent creation&deletion.



### HOW TO EVALUATE THE RESULTS-
     1. DEFINITIONS AND FORMULAE:-
          (TP-> TruePositive, FP->FalsePositive, TN-> TrueNegative, FN-> FalseNegative)
          TP of intent->  output intent is current intent and expected is current intent (matched current intent)
          FP of intent->  output intent is current intent but Expected intent is different
          FN of intent->  Expected is current intent but output intent is different
          TN of intent->  output intent and expected intent is not current intent

          TP of intents = sum of all TP of intents except None
          FP of intents = sum of all FP of intents except None
          TN of intents = sum of all TN of intents except None
          FN of intents = sum of all FN of intents except None


```
          Precision = (TP of intents + TP of None)/( (TP of intents + TP of None) + FP of intents )

          Recall = (TP of intents + TP of None)/( (TP of intents + TP of None) + FN of intents )

          Fmeasure = 2*(TP of intents + TP of None)/( 2*(TP of intents + TP of None) + FN of intents + FP of intents )

          Accuracy = (TP of intents + TP of None)/( (TP of intents + TP of None) + FN of intents + FP of intents )
```
     2. The Results sheet has the status pass or fail depending on the intent identified matched with expected intent.
     3. The Summary sheet shows Precision, Recall, F Measure and Accuracy Values for all the three platforms.
     4. The IndividualIntents sheet shows the True Positives, True Negatives, False Positives and False Negatives for all the three platforms for individual tasks.
     5. Ambiguity cases are shown in the results and are counted towards None intent.

NOTES- Certain limitations are to be noted:
	a. Maximum number of Intents that can be created in Luis.AI are 12.
	b. Maximum number of endpoint hits for Luis.AI are 1000 hits per month for an account(For all the bots in the account together)
	c. Maximum number of agents that can be created in API.AI are 15


Sample : Previously run results can be found at https://github.com/Koredotcom/NLP-Benchmark/blob/8c418a26d0c1944a6222968731f5e168dd403cbf/previous-test-results/ML_Results-Benchmark_Banking77_KORE-08-01-2021--22-43-34.xlsx

# Citations of Benchmark datasets available in the repo

1. Banking77
### Citations

[Efficient Intent Detection with Dual Sentence Encoders](https://arxiv.org/abs/2003.04807).

```bibtex
@inproceedings{Casanueva2020,
    author      = {I{\~{n}}igo Casanueva and Tadas Temcinas and Daniela Gerz and Matthew Henderson and Ivan Vulic},
    title       = {Efficient Intent Detection with Dual Sentence Encoders},
    year        = {2020},
    month       = {mar},
    note        = {Data available at https://github.com/PolyAI-LDN/task-specific-datasets},
    url         = {https://arxiv.org/abs/2003.04807},
    booktitle   = {Proceedings of the 2nd Workshop on NLP for ConvAI - ACL 2020}
}

```