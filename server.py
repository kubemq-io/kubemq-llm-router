import time
from kubemq.cq import *
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
import threading

load_dotenv()


class LLMRouter:
    def __init__(self):
        self.openai_llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo"
        )
        self.claude_llm = ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model_name="claude-3-sonnet-20240229"
        )
        self.client = Client(address="localhost:50000")

    def handle_openai_query(self, request: QueryMessageReceived):
        try:
            message = request.body.decode('utf-8')
            result = self.openai_llm.invoke(message).content
            response = QueryResponseMessage(
                query_received=request,
                is_executed=True,
                body=result.encode('utf-8')
            )
            self.client.send_response_message(response)
        except Exception as e:
            self.client.send_response_message(QueryResponseMessage(
                query_received=request,
                is_executed=False,
                error=str(e)
            ))

    def handle_claude_query(self, request: QueryMessageReceived):
        try:
            message = request.body.decode('utf-8')
            result = self.claude_llm.invoke(message).content
            response = QueryResponseMessage(
                query_received=request,
                is_executed=True,
                body=result.encode('utf-8')
            )
            self.client.send_response_message(response)
        except Exception as e:
            self.client.send_response_message(QueryResponseMessage(
                query_received=request,
                is_executed=False,
                error=str(e)
            ))

    def run(self):
        def on_error(err: str):
            print(f"Error: {err}")

        def subscribe_openai():
            self.client.subscribe_to_queries(
                subscription=QueriesSubscription(
                    channel="openai_requests",
                    on_receive_query_callback=self.handle_openai_query,
                    on_error_callback=on_error,
                ),
                cancel=CancellationToken()
            )

        def subscribe_claude():
            self.client.subscribe_to_queries(
                subscription=QueriesSubscription(
                    channel="claude_requests",
                    on_receive_query_callback=self.handle_claude_query,
                    on_error_callback=on_error,
                ),
                cancel=CancellationToken()
            )

        threading.Thread(target=subscribe_openai).start()
        threading.Thread(target=subscribe_claude).start()

        print("LLM Router running on channels: openai_requests, claude_requests")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    router = LLMRouter()
    router.run()