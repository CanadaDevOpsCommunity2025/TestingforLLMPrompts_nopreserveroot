import random
import yaml
import json
import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# Load from .env file if available
load_dotenv()

# Updated imports to avoid warnings
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI

# Debug: show working dir
print("Current working directory:", os.getcwd())

# Check the API key
if "OPENAI_API_KEY" not in os.environ:
    print("OPENAI_API_KEY is not set! Set it in .env or environment.")
    exit(1)

# Load prompts from YAML
def load_prompts_by_category(filepath="prompts.yaml"):
    if not os.path.isfile(filepath):
        print(f" File not found: {filepath}")
        exit(1)
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return data["prompts_by_category"]

# Setup LangChain chains
def create_chains_by_category(prompts_by_category):
    llm = OpenAI(temperature=0.7)
    chains = {}
    for category, prompts in prompts_by_category.items():
        chains[category] = {}
        for variant_key, prompt_info in prompts.items():
            template = PromptTemplate.from_template(prompt_info["template"])
            chains[category][variant_key] = {
                "description": prompt_info["description"],
                "chain": LLMChain(prompt=template, llm=llm)
            }
    return chains

# Intent classification
def classify_intent(user_input: str) -> str:
    user_input_lower = user_input.lower()
    if "return" in user_input_lower or "refund" in user_input_lower:
        return "returns"
    elif "price" in user_input_lower or "specs" in user_input_lower:
        return "product_info"
    else:
        return "general"

# Handle user request
def handle_user_request(user_id: int, user_input: str, chains_by_category):
    intent_category = classify_intent(user_input)
    category_chains = chains_by_category.get(intent_category)
    prompt_key = random.choice(list(category_chains.keys()))
    chain_info = category_chains[prompt_key]
    response = chain_info["chain"].run({"user_input": user_input})
    log_entry = {
        "timestamp": str(datetime.datetime.utcnow()),
        "user_id": user_id,
        "user_input": user_input,
        "intent_category": intent_category,
        "prompt_variant": prompt_key,
        "prompt_description": chain_info["description"],
        "llm_response": response
    }
    log_df = pd.DataFrame([log_entry])
    log_df.to_csv("logs.csv", mode="a", header=not os.path.isfile("logs.csv"), index=False)
    return response, log_entry

# Example usage
if __name__ == "__main__":
    prompts_by_category = load_prompts_by_category()
    chains_by_category = create_chains_by_category(prompts_by_category)

    user_id = 101
    user_input = "I’d like to return a defective product."
    response, log_entry = handle_user_request(user_id, user_input, chains_by_category)

    print("\n✅ Generated LLM Response:\n", response)
    print("\n📄 Log Entry:\n", json.dumps(log_entry, indent=2))
