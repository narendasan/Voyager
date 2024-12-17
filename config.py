import os

def prompt_api_key():
    """Prompt the user for their OpenAI API key without displaying input."""
    import getpass
    while True:
        api_key = getpass.getpass("Enter your OpenAI API key: ").strip()
        if api_key:
            return api_key
        print("API key cannot be empty. Please try again.")

def select_model():
    """Prompt the user to select an OpenAI model from a predefined list."""
    models = ["gpt-4", "gpt-4o", "gpt-4o-mini"]
    print("\nAvailable OpenAI models:")
    for i, model in enumerate(models, start=1):
        print(f"{i}. {model}")
    
    while True:
        choice = input("\nSelect a model by entering the corresponding number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            return models[int(choice) - 1]
        print("Invalid selection. Please enter a number corresponding to the available models.")

def write_env_file(api_key, model):
    """Write the OpenAI API key and model to a .env file."""
    env_content = f"""OPENAI_API_KEY="{api_key}"

# o1 models are not supported
OPENAI_MODEL="{model}"
"""
    with open(".env", "w") as file:
        file.write(env_content)
    print("\n✅ .env file created successfully!")

def main():
    api_key = prompt_api_key()
    model = select_model()
    write_env_file(api_key, model)
    print("\nYour configuration has been saved in '.env'.")

if __name__ == "__main__":
    main()
