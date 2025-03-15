import os
import json
import yaml


RUN_PATH = os.environ.get("RUN_PATH", os.path.dirname(os.path.abspath(__file__)))

with open(RUN_PATH + "/config.yaml", "r") as file:
    data = yaml.safe_load(file)

LLM_PROXY_AGENT = data["llm_proxy_agent"]
