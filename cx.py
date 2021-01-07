import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import os, time, uuid, sys
from tqdm import tqdm
from google.cloud import dialogflowcx as df
from google.protobuf.field_mask_pb2 import FieldMask
from sklearn.metrics import precision_recall_fscore_support
from configBot import *
from dfConfig import *
intents_client  = df.IntentsClient()
flows_client = df.FlowsClient()
SESSION_ID = "UUID('813674c2-7b81-4ba0-a2fd-2e090666b17d')"


def get_intent_list(agent):
	df_intents = {}
	listIntents = df.ListIntentsRequest(parent=agent)
	intents = intents_client.list_intents(listIntents)
	for intent in intents:
		df_intents[intent.display_name] = intent
	return df_intents

def delete_intent(intent):
	print(intent.display_name, intent.name)
	if "00000000-0000-0000-0000-" in intent.name:
		return
	deleteInent = df.DeleteIntentRequest(name=intent.name)
	intents_client.delete_intent(deleteInent)
	print("deleted",intent.display_name, intent.name)
	time.sleep(1)


def delete_all_intents(intents):
	for intent_name, intent in intents.items():
		delete_intent(intent)

def create_intent(agent, intent_name):
	intent = df.Intent(
		display_name = intent_name
	)
	createIntent = df.CreateIntentRequest(intent=intent, parent=agent)
	intent = intents_client.create_intent(createIntent)
	time.sleep(1)
	return intent

def add_training_data(intents, train_data):
	for i, row in train_data.iterrows():
		part = df.Intent.TrainingPhrase.Part(text = row[TEXT_COLUMN])
		training_phrase = df.Intent.TrainingPhrase(parts=[part], repeat_count=1)
		intent = intents[row[INTENT_COLUMN]]
		intent.training_phrases.extend([training_phrase])
	for df_intent in tqdm(intents, desc="adding training data"):
		updateIntent = df.UpdateIntentRequest(intent=intents[df_intent])
		response  = intents_client.update_intent(updateIntent)
		time.sleep(1)

def detect_intent(agent, text_input):
	try:
		text_input = text_input[:255] #dialog 
		DIALOGFLOW_LANGUAGE_CODE = "en"
		session_path = f"{agent}/sessions/{SESSION_ID}"
		session_client = df.SessionsClient()
		text_input = df.TextInput(text=text_input)
		query_input = df.QueryInput(text=text_input, language_code=DIALOGFLOW_LANGUAGE_CODE)
		query_params = df.QueryParameters(parameters ={"resetContexts": True})
		detectIntent = df.DetectIntentRequest(session=session_path,query_params=query_params,query_input=query_input)
		response = session_client.detect_intent(request=detectIntent)
		return response.query_result.intent.display_name,response.query_result.intent_detection_confidence
	except Exception as e:
		print("exception while input")
		print(text_input)
		print("Unexpected error:", sys.exc_info()[0])
		return "",""


def create_agent(agent_name, location_path):
	agent = df.Agent(display_name=agent_name, default_language_code=LANGUAGE_CODE, time_zone=TIME_ZONE)
	createAgentRequest = df.CreateAgentRequest(agent=agent, parent=location_path)
	agentsClient = df.AgentsClient()
	agent = agentsClient.create_agent(request=createAgentRequest)
	return agent

def create_all_intents(agent, train_data):
	print("creating intents")
	df_intents = get_intent_list(agent)
	intent_names = train_data[INTENT_COLUMN].unique()
	for intent_name in intent_names:
		if intent_name in df_intents:
			continue
		print(intent_name)
		intent = create_intent(agent, intent_name)
		df_intents[intent_name] = intent
	add_training_data(df_intents, train_data)

def do_test(agent, test_data):
	#test_data = test_data[:10]
	actuals = []
	expected = []
	for i, row in tqdm(test_data.iterrows()):
		text_input = row[TEXT_COLUMN]
		intent_name = row[INTENT_COLUMN]
		expected.append(intent_name)
		actual_intent = detect_intent(agent, text_input)
		if actual_intent.strip() == "":
			actual_intent = "None"
		actuals.append(actual_intent)
	print("type, precision, recall, fscore, support")
	precision, recall, fscore, support = precision_recall_fscore_support(expected, actuals, average="micro")
	print("micro", precision, recall, fscore, support)
	precision, recall, fscore, support = precision_recall_fscore_support(expected, actuals, average="weighted")
	print("weighted", precision, recall, fscore, support)
	precision, recall, fscore, support = precision_recall_fscore_support(expected, actuals, average="macro")
	print("macro", precision, recall, fscore, support)
	test_data["actual"] = actuals
	success_series = test_data["actual"] == test_data[INTENT_COLUMN]
	total_count = len(test_data)
	success_count = len(test_data[success_series])
	success_ratio = round(success_count/total_count, 2)
	print("total", total_count, "success", success_count, "success %", success_ratio)
	test_data.to_csv("results.csv",index=False)

def get_flow(agent, flowId):
	flowPath = f"{agent}/flows/{flowId}"
	flowRequest = df.GetFlowRequest(name=flowPath)
	flow = flows_client.get_flow(flowRequest)
	return flow

def update_transition_routes(flow, intents):
	routes = flow.transition_routes
	existing_routes = set()
	for route in routes:
		intent_name = route.intent
		existing_routes.add(intent_name)

	for intent_name, intent in intents.items():
		if intent.name in existing_routes:
			continue
		if "00000000-0000-0000" in intent.name:
			continue
		resText = df.ResponseMessage.Text(text=[f"{intent_name} intent"])
		rm = df.ResponseMessage(text=resText)
		ff = df.Fulfillment(messages=[rm])
		route = df.TransitionRoute(intent=intent.name, trigger_fulfillment=ff)
		flow.transition_routes.append(route)
		existing_routes.add(intent.name)
	mask = FieldMask()
	mask.FromJsonString("transitionRoutes")
	flowRequest = df.UpdateFlowRequest(flow=flow, update_mask=mask)
	flows_client.update_flow(request=flowRequest)
	#print(flow.transition_routes)

def update_nlu_type(flow, nlu_type):
	flowPath = flow.name
	#nlu_settings = df.NluSettings(model_type=nlu_type)
	flow.nlu_settings.model_type = nlu_type
	mask = FieldMask()
	mask.FromJsonString("nluSettings")
	flowRequest = df.UpdateFlowRequest(flow=flow, update_mask=mask)
	flows_client.update_flow(request=flowRequest)

def train_flow(flow):
	print("training started")
	trainFlowRequest = df.TrainFlowRequest(name=flow.name)
	flowsClient = df.FlowsClient()
	train_operation = flowsClient.train_flow(request=trainFlowRequest)
	result = train_operation.result()
	print("training Completed")

def create_and_test():
	locationPath = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}"
	print("creating agent", AGENT_NAME)
	agent = create_agent(AGENT_NAME, locationPath)
	print("agent created", agent.name)
	train_data = pd.read_csv(TRAIN_FILE)
	create_all_intents(agent.name, train_data)
	df_intents = get_intent_list(agent.name)
	flow = get_flow(agent.name, DEFAULT_FLOW_ID)
	update_transition_routes(flow, df_intents)
	# update_nlu_type(flow, df.NluSettings.ModelType.MODEL_TYPE_ADVANCED)
	update_nlu_type = (flow,df.NluSettings.ModelType.MODEL_TYPE_STANDARD)
	train_flow(flow)
	test_data = pd.read_csv(TEST_FILE)
	do_test(agent.name, test_data)

def test_existing(train=False):
	agent_name = input("give me agent Id")
	agent_name = agent_name.strip().lower()
	locationPath = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}"
	print("getting agents at location", locationPath)
	agentsClient = df.AgentsClient()
	listAgentsRequest = df.ListAgentsRequest(parent=locationPath)
	agents = agentsClient.list_agents(request=listAgentsRequest).agents
	agent = None
	for a in agents:
		print(a.name, a.display_name)
		name = a.display_name.lower()
		if name == agent_name:
			agent = a
			break
	if train:
		flow = get_flow(agent.name, DEFAULT_FLOW_ID)
		train_flow(flow)
		pass
	test_data = pd.read_csv(TEST_FILE)
	do_test(agent.name, test_data)

def getAgent(botname):
	agent_name = botname.strip().lower()
	locationPath = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}"
	print("getting agents at location", locationPath)
	agentsClient = df.AgentsClient()
	listAgentsRequest = df.ListAgentsRequest(parent=locationPath)
	agents = agentsClient.list_agents(request=listAgentsRequest).agents
	agent = None
	for a in agents:
		print(a.name, a.display_name)
		name = a.display_name.lower()
		if name == agent_name:
			agent = a
			break
	return agent


def delete_agent():
	agent_name = input("give me agent Id")
	agent_name = agent_name.strip().lower()
	locationPath = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}"
	print("getting agents at location", locationPath)
	agentsClient = df.AgentsClient()
	listAgentsRequest = df.ListAgentsRequest(parent=locationPath)
	agents = agentsClient.list_agents(request=listAgentsRequest).agents
	deleteAgent = None
	for agent in agents:
		print(agent.name, agent.display_name)
		name = agent.display_name.lower()
		if name == agent_name:
			deleteAgent = agent
	deleteAgentRequest = df.DeleteAgentRequest()
	deleteAgentRequest.name=deleteAgent.name
	agentsClient.delete_agent(request=deleteAgentRequest)
	print("agent deleted", deleteAgent.name)


		



if __name__ == "__main__":
	create_and_test()
	#test_existing()
	#delete_agent()
	
	
	
	'''delete_intents = input("Do you want to delete intents first?")
	if delete_intents.strip().lower() in ["y", "yes", "yeah", "sure"]:
		df_intents = get_intent_list(agentPath)
		delete_all_intents(df_intents)
	create_all_intents(agentPath)'''
	#test_data = pd.read_csv(TEST_FILE)
	#do_test(agentPath, test_data)
	#df_intents = get_intent_list()
	#flow = get_flow()
	#update_transition_routes(flow, df_intents)
	#flow = get_flow()
	#print(flow)
	#print("\n\n\n")
	#print(flow.transition_routes)
	#print(type(flow.transition_routes[0]))

