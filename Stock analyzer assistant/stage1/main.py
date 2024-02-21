import os
import time

from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.threads.run import Run
from openai.types.beta.thread import Thread
from openai.types.beta.threads.thread_message import ThreadMessage
from openai.pagination import SyncCursorPage
from typing import Optional, List


class OpenAIAssistantsAPI:
    def __init__(self, _openai_api_key: str, _openai_model: str):
        self._openai_model = _openai_model
        self._openai_client = OpenAI(api_key=_openai_api_key)

    def create_assistant(self, name: str, instructions: str) -> Assistant:
        return self._openai_client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=self._openai_model,
        )

    def assistant_exists(self, name: str) -> bool:
        existing_assistants = self.list_assistants()
        return any(assistant.name == name for assistant in existing_assistants)

    def get_assistant_id_by_name(self, name: str) -> str | None:
        existing_assistants = self.list_assistants()
        for assistant in existing_assistants:
            if assistant.name == name:
                return assistant.id
        return None

    def list_assistants(self) -> List[Assistant]:
        assistants = self._openai_client.beta.assistants.list()
        return assistants.data

    def retrieve_assistant(self, assistant_id: str) -> Assistant:
        return self._openai_client.beta.assistants.retrieve(assistant_id)

    def run_assistant(self, assistant_id: str, thread_id: str,
                      assistant_name: Optional[str] = "", instructions: Optional[str] = None) -> Run:
        if instructions is not None:
            run = self._openai_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                instructions=instructions,
            )
        else:
            run = self._openai_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )

        run = self.wait_on_run(run, thread_id, assistant_name)
        return run

    def wait_on_run(self, run, thread_id, assistant_name="") -> Run:
        start_time = time.time()
        print(f"Run initiated with ID: {run.id}")
        print(f"Waiting for response from `{assistant_name}` Assistant.", end="")
        while run.status in ["queued", "in_progress"]:
            elapsed_time = time.time() - start_time
            print(f"\rWaiting for response from `{assistant_name}` Assistant. Elapsed time: {elapsed_time:.2f} seconds",
                  end="", flush=True)
            time.sleep(1)
            run = self._openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nDone! Response received in {total_time:.2f} seconds.\n")
        return run

    def create_thread(self) -> Thread:
        return self._openai_client.beta.threads.create()

    def send_message_to_thread(self, thread_id: str, content: str):
        self._openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
        )

    def get_thread_messages(self, thread_id: str) -> SyncCursorPage[ThreadMessage]:
        return self._openai_client.beta.threads.messages.list(thread_id=thread_id)


def main():
    # Initialize the OpenAIAssistantsAPI with your OpenAI API key and the desired model
    # You must first Set the OpenAI API key as an environment variable
    # and then use os.getenv("OPENAI_API_KEY") to retrieve it:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = "gpt-3.5-turbo"
    openai_assistants_api = OpenAIAssistantsAPI(_openai_api_key=openai_api_key, _openai_model=openai_model)

    # Step 1: Set up the Assistant name and instructions
    assistant_name = "stock_analyzer_assistant"
    instructions = "Analyze and visualize stock market data."

    # Step 2: Check if the Assistant already exists and create it if it does not
    if not openai_assistants_api.assistant_exists(assistant_name):
        stock_analyzer_assistant = openai_assistants_api.create_assistant(
            name=assistant_name,
            instructions=instructions
        )
        print(
            f"No matching `{assistant_name}` assistant found, "
            f"creating a new assistant with ID: {stock_analyzer_assistant.id}")
    else:
        assistant_id = openai_assistants_api.get_assistant_id_by_name(assistant_name)
        stock_analyzer_assistant = openai_assistants_api.retrieve_assistant(assistant_id)
        print(
            f"Matching `{assistant_name}` assistant found, "
            f"using the first matching assistant with ID: {stock_analyzer_assistant.id}")

    # Step 3: Create a Thread for the conversation
    thread = openai_assistants_api.create_thread()
    print(f"Thread created with ID: {thread.id}")

    # Step 4: Send a message with a prompt to the Thread
    prompt = "Tell me your specific name, and instructions. Provide a DIRECT and SHORT response."
    openai_assistants_api.send_message_to_thread(thread_id=thread.id, content=prompt)

    # Step 5: Execute a Run instance with the Assistant to process the prompt sent to the Thread
    run = openai_assistants_api.run_assistant(
        assistant_id=stock_analyzer_assistant.id,
        thread_id=thread.id,
        assistant_name=assistant_name
    )
    print(f"Run initiated with ID: {run.id}")

    # The output of the assistant won't be checked, but we can think of additional test cases to maybe check it?
    # stock_analyzer_assistant_messages = openai_assistants_api.get_thread_messages(thread.id)
    # stock_analyzer_assistant_response = stock_analyzer_assistant_messages.data[0].content[0].text.value
    #
    # print(f"Assistant response: {stock_analyzer_assistant_response}")


if __name__ == "__main__":
    main()
