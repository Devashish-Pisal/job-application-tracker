import requests

'''
MODELS TO USE:

- Llama 3.1 8B
- Mistral
- Phi-3 Mini 


PARAMs:
    temperature: 0
    top_p: 0.1
    repeat_penalty: 1.1

'''


def call_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]