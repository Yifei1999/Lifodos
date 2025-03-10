import os
import json
import yaml


RUN_PATH = os.environ.get("RUN_PATH", os.path.dirname(os.path.abspath(__file__)))

with open(RUN_PATH + "/config.yaml", "r") as file:
    data = yaml.safe_load(file)

llm_agent_name = data["llm_proxy_agent"]["activated_name"]
llm_agent_config = data["llm_proxy_agent"][llm_agent_name]
LLM_PROXY_AGENT = data["llm_proxy_agent"]
