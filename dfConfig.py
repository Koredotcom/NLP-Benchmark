import os, uuid, json

with open("dfConfig.json", "r") as fp:
	conf = json.load(fp)

SERVICE_ACCOUNT_FILE = conf.get("SERVICE_ACCOUNT_FILE_PATH", None)
PROJECT_ID = conf.get("PROJECT_ID", None)
LOCATION_ID = conf.get("LOCATION_ID", "global")
# AGENT_ID = "id of the agent"
LANGUAGE_CODE = "en-us"
TIME_ZONE="America/New_York"
DEFAULT_FLOW_ID = "00000000-0000-0000-0000-000000000000"

# agentPath = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{AGENT_ID}"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

# AGENT_NAME = "mytestagent6"

# TRAIN_FILE = "data/AskUbuntuCorpus_train.csv"
# TEST_FILE = "data/AskUbuntuCorpus_test.csv"
INTENT_COLUMN = "intent"
TEXT_COLUMN = "input"