import random
import yaml
import json
import datetime
import pandas as pd
import os

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI

# Check that the API key is set
if "OPENAI_API_KEY" not in os.environ:
    print("The environment variable 'OPENAI_API_KEY' is not set!")
    print("Please set it (Windows example): setx OPENAI_API_KEY \"sk-YourKeyHere\"")
    exit(1)

# Load prompts from YAML (now structured by category!)
def load_prompts_by_category(filepath="prompts.yaml"):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        print("Please make sure 'prompts.yaml' is in the same directory as this script.")
        exit(1)

    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return data["prompts_by_category"]

# Set up LangChain chains for each prompt variant in each category
def create_chains_by_category(prompts_by_category):
    # Initialize the OpenAI LLM (it will read the key from the environment)
    llm = OpenAI(
        temperature=0.7,
    )

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

# A simple intent classifier
def classify_intent(user_input: str) -> str:
    user_input_lower = user_input.lower()
    if "return" in user_input_lower or "refund" in user_input_lower:
        return "returns"
    elif "price" in user_input_lower or "specs" in user_input_lower:
        return "product_info"
    else:
        return "general"

# Handle a real user request
def handle_user_request(user_id: int, user_input: str, chains_by_category):
    # Classify intent to choose category
    intent_category = classify_intent(user_input)
    print(f"User intent classified as: {intent_category}")

    # Get available prompt variants for the category
    category_chains = chains_by_category.get(intent_category)
    if not category_chains:
        print(f"No prompts defined for intent category: {intent_category}")
        exit(1)

    # Randomly choose a variant
    prompt_key = random.choice(list(category_chains.keys()))
    chain_info = category_chains[prompt_key]

    # Generate LLM response
    response = chain_info["chain"].run({"user_input": user_input})

    # Log to CSV
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
