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
    # Use the LLM to classify user input dynamically
    # We'll prompt the LLM to choose one of the predefined categories
    classification_prompt = (
        "You are an intent classification assistant.\n"
        "Classify the following user query into one of these categories:\n"
        "- returns\n"
        "- product_info\n"
        "- general\n"
        "Respond only with the category name (no explanation).\n\n"
        f"User query: \"{user_input}\"\n"
        "Category:"
    )

    # Use a dedicated OpenAI instance for classification if you want (or reuse the same)
    classifier_llm = OpenAI(temperature=0)  # More deterministic for classification
    category = classifier_llm.invoke(classification_prompt).strip().lower()

    # Validate that the category is one of the expected ones (fallback to general)
    if category not in {"returns", "product_info", "general"}:
        print(f"Unexpected category from LLM: {category}, defaulting to 'general'")
        return "general"

    print(f" LLM classified intent as: {category}")
    return category


# Handle user request
def handle_user_request(user_id: int, user_input: str, chains_by_category):
    # Classify intent
    intent_category = classify_intent(user_input)
    category_chains = chains_by_category.get(intent_category)

    # Generate responses for all prompt variants (A/B)
    variant_responses = {}
    for prompt_key, chain_info in category_chains.items():
        response = chain_info["chain"].run({"user_input": user_input})
        variant_responses[prompt_key] = {
            "response": response,
            "description": chain_info["description"]
        }

    # Let LLM compare and decide the best one
    comparison_prompt = (
        f"You are an evaluation assistant.\n"
        f"Given the user's query: \"{user_input}\"\n\n"
        f"Here are two response options:\n"
        f"A ({category_chains['A']['description']}): {variant_responses['A']['response']}\n"
        f"B ({category_chains['B']['description']}): {variant_responses['B']['response']}\n\n"
        f"Choose the best response (A or B) and respond with only the letter (no explanation)."
    )

    evaluator_llm = OpenAI(temperature=0)
    best_option = evaluator_llm.invoke(comparison_prompt).strip().upper()

    # Validate best option (fallback to A)
    if best_option not in {"A", "B"}:
        print(f"Unexpected evaluator response: {best_option}, defaulting to A")
        best_option = "A"

    # Prepare log
    log_entry = {
        "timestamp": str(datetime.datetime.utcnow()),
        "user_id": user_id,
        "user_input": user_input,
        "intent_category": intent_category,
        "chosen_variant": best_option,
        "prompt_A": variant_responses['A'],
        "prompt_B": variant_responses['B']
    }

    log_df = pd.DataFrame([log_entry])
    log_df.to_csv("logs.csv", mode="a", header=not os.path.isfile("logs.csv"), index=False)

    # Return best response
    best_response = variant_responses[best_option]["response"]
    print(f"\n Best response selected by LLM: {best_option}")
    return best_response, log_entry

def add_new_prompt_to_category(filepath="prompts.yaml"):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    categories = list(data["prompts_by_category"].keys())
    print("\nAvailable categories:")
    for idx, cat in enumerate(categories, start=1):
        print(f"{idx}. {cat}")

    cat_choice = int(input("Select a category by number to add a new prompt to:\n> ")) - 1
    category = categories[cat_choice]

    description = input("Enter a short description for the new prompt:\n> ").strip()
    template = input("Enter the actual prompt template (use {user_input} where needed):\n> ").strip()

    # Determine the next variant key (e.g., C, D, etc.)
    existing_variants = data["prompts_by_category"][category].keys()
    next_variant = chr(ord(max(existing_variants)) + 1)

    data["prompts_by_category"][category][next_variant] = {
        "description": description,
        "template": template
    }

    with open(filepath, "w") as f:
        yaml.dump(data, f, sort_keys=False)

    print(f" New prompt added under category '{category}' with key '{next_variant}'.")

# usage
if __name__ == "__main__":
    prompts_by_category = load_prompts_by_category()
    chains_by_category = create_chains_by_category(prompts_by_category)

    print("\nWhat would you like to do?")
    print("1. Use existing prompts for your query")
    print("2. Add a new prompt to a category")

    choice = input("\nSelect an option (1 or 2):\n> ").strip()

    if choice == "1":
        user_id = 101
        user_input = input("\nPlease enter your query:\n> ").strip()
        response, log_entry = handle_user_request(user_id, user_input, chains_by_category)
        print("\n Generated LLM Response:\n", response)
        print("\n Log Entry:\n", json.dumps(log_entry, indent=2))
    elif choice == "2":
        add_new_prompt_to_category()
    else:
        print(" Invalid choice! Exiting.")
