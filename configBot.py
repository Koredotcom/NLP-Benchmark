#Configuration for API.ai
#First of all create a new bot(referred as agent in api.ai). Press on the gear icon on the left next to the bot name. Copy the Developer_Access_Token and paste it within the quotes of Token_Api.
Token_Api="XXXXXXXXXX"
#In the URL of the page, copy the id next to 'editAgent/' and paste it within the quotes in botIDApi.
botIDApi="XXXXXXXXXX"



#Configuration for Luis.ai
#As soon as you login into the Luis website, press on My Keys. In this page, copy the Programmatic API key and paste it within the keys in subscriptionToken.
subscriptionToken="XXXXXXXXXXX"


headerLuis={ 
        'ocp-apim-subscription-key': subscriptionToken,
        'content-type': "application/json; charset=UTF-8",
}


#Configuration for Kore.ai
#Enter the name for the environment to be run in within quotes in korePlatform.  
KorePlatform="XXXXXXX"
#If running with company account id, please mark ssoKore as 'True' and enter the user-ID along with Authorization bearer in the command prompt. Else, enter you credentials in the terminal.
ssoKore=False
#Name of the input file.
fileName='intent.csv'
headersKore = {
        'content-type': "application/json;charset=UTF-8",
}
