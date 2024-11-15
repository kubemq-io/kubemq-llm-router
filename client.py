from kubemq.cq import *
import json


class LLMClient:
    def __init__(self, address="localhost:50000"):
        self.client = Client(address=address)

    def send_message(self, message: str, model: str) -> dict:
        channel = f"{model}_requests"
        response = self.client.send_query_request(QueryMessage(
            channel=channel,
            body=message.encode('utf-8'),
            timeout_in_seconds=30
        ))
        return json.loads(response.body) if response.body else {"error": response.error}


if __name__ == "__main__":
    client = LLMClient()
    models = ["openai", "claude"]
    message = input("Enter your message: ")
    model = input(f"Choose model ({'/'.join(models)}): ")
    if model in models:
        response = client.send_message(message, model)
        print(f"Response: {response['response']}")
    else:
        print("Invalid model selected")