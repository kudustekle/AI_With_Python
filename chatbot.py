from transformers import pipeline

# Load GPT-2 Model (Offline)
chat_model = pipeline("text-generation", model="gpt2")

def chat_response(user_input):
    """Generates a response using GPT-2"""
    response = chat_model(user_input, max_length=200, do_sample=True)
    return response[0]['generated_text']
