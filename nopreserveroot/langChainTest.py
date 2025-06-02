import random
import yaml
import json
import datetime
import pandas as pd  # For CSV logging
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# 1️⃣ Load prompts from YAML
def load_prompts(filepath="prompts.yaml"):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return data["prompts"]

# 2️⃣ Set up LangChain chains
def create_chains(prompts_dict):
    llm = OpenAI(temperature=0.7)
    chains = {}
    for key, prompt_info in prompts_dict.items():
        template = PromptTemplate.from_template(prompt_info["template"])
        chains[key] = {
            "description": prompt_info["description"],
            "chain": LLMChain(prompt=template, llm=llm)
        }
    return chains

# 3️⃣ Handle a real user request
def handle_user_request(user_id: int, user_input: str, chains):
    # Randomly choose a system prompt variant
    prompt_key = random.choice(list(chains.keys()))
    chain_info = chains[prompt_key]

    # Generate LLM response
    response = chain_info["chain"].run({"user_input": user_input})

    # Log to CSV (append)
    log_entry = {
        "timestamp": str(datetime.datetime.utcnow()),
        "user_id": user_id,
        "user_input": user_input,
        "prompt_variant": prompt_key,
        "prompt_description": chain_info["description"],
        "llm_response": response
    }

    # Save to CSV
    log_df = pd.DataFrame([log_entry])
    log_df.to_csv("logs.csv", mode="a", header=not pd.io.common.file_exists("logs.csv"), index=False)

    return response, log_entry

# 4️⃣ Example usage
if __name__ == "__main__":
    prompts = load_prompts()
    chains = create_chains(prompts)

    user_id = 101
    user_input = "I’d like to return a defective product."
    response, log_entry = handle_user_request(user_id, user_input, chains)

    print("\nGenerated LLM Response:\n", response)
    print("\nLog Entry:\n", json.dumps(log_entry, indent=2))
