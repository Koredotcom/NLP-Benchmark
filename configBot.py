#Configuration for API.ai -:

#First of all create a new bot(referred as agent in api.ai). Press on the gear icon on the left next to the bot name. Copy the Developer_Access_Token and paste it within the quotes of Token_Api.

Token_Api="ad909svfv7sdf8bc254ddsdfs86569"

#In the URL of the page, copy the id next to 'editAgent/' and paste it within the quotes in botIDApi.

botIDApi="4rdfg5-febd-455e-a272-69c7d5772824"


#Configuration for Luis.ai -:

#As soon as you login into the Luis website, press on My Keys. In this page, copy the Programmatic API key and paste it within the keys in subscriptionToken.

subscriptionToken="42a6a52ad33140ff9da0054563eff162"


#Configuration for Kore.ai -:

#Enter the name of the environment for which the Benchmark tool needs to be run within the quotes in korePlatform.  

KorePlatform="bots.kore.ai"

#If running with company account id, please mark ssoKore as 'True' and enter the user-ID along with Authorization bearer in the command prompt. Else, enter you login credentials in the terminal.

ssoKore=False

#Name of the input file which contains Intent names of Intents to be created as well as the utterances to be trained for the respective intents.


fileName='ML_Train.csv'
headerLuis={ 
        'ocp-apim-subscription-key': subscriptionToken,
        'content-type': "application/json; charset=UTF-8",
}
headersKore = {
        'content-type': "application/json;charset=UTF-8",
}

USEGOOGLE=False
USELUIS=False
