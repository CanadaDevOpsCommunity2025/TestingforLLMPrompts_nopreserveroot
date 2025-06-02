# langchain_skeleton_categorized.py

import random
import json
import datetime
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# 1️⃣ Predefined system prompts
prompt_templates = {
    "A": PromptTemplate.from_template(
        "You are a polite customer support agent. Provide a concise answer to: {user_input}"
    ),
    "B": PromptTemplate.from_template(
        "You are a friendly assistant. Provide a detailed and supportive response to: {user_input}"
    ),
    "C": PromptTemplate.from_template(
        "You are a concise technical assistant. Provide a brief and direct answer to: {user_input}"
    )
}

# 2️⃣ Simple intent classifier
def classify_intent(user_input: str) -> str:
    user_input_lower = user_input.lower()
    if "return" in user_input_lower or "refund" in user_input_lower:
        return "returns"
    elif "price" in user_input_lower or "specs" in user_input_lower:
        return "product_info"
    else:
        return "general"

# 3️⃣ Map intents to allowed prompts
intent_to_prompts = {
    "returns": ["A", "C"],
    "product_info": ["B"],
    "general": ["A", "B", "C"]
}

# 4️⃣ Initialize LangChain LLM
llm = OpenAI(temperature=0.7)
chains = {key: LLMChain(prompt=prompt, llm=llm) for key, prompt in prompt_templates.items()}

# 5️⃣ Core function to handle user input
def handle_user_request(user_id: int, user_input: str):
    # Classify user intent
    intent = classify_intent(user_input)
    valid_prompts = intent_to_prompts[intent]

    # Pick a prompt within the category (can also rotate for even testing)
    prompt_key = random.choice(valid_prompts)
    chain = chains[prompt_key]

    # Generate LLM response
    response = chain.run({"user_input": user_input})

    # Log results for later analysis
    log_entry = {
        "timestamp": str(datetime.datetime.utcnow()),
        "user_id": user_id,
        "user_input": user_input,
        "intent": intent,
        "prompt_variant": prompt_key,
        "llm_response": response
    }

    with open("logs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return response

# 6️⃣ Example usage
if __name__ == "__main__":
    user_id = 42
    user_input = "I want to return a product, can you help?"
    response = handle_user_request(user_id, user_input)
    print("\nGenerated LLM Response:\n", response)
