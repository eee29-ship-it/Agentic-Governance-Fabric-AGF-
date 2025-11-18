import vertexai
from vertexai import agent_engines
import time

# ------------------------------------------
# CONFIG — PUT YOUR VALUES HERE
# ------------------------------------------
PROJECT_ID = "163991862440"
LOCATION = "us-central1"

ENGINE_RESOURCE_ID = (
    "projects/163991862440/locations/us-central1/reasoningEngines/2773526877157982208"
)
USER_ID = "poc-user"

# ------------------------------------------
# HELPER: Wait for engine readiness
# ------------------------------------------
def wait_for_engine_ready(engine, timeout=30, poll_interval=2):
    """
    Waits until the engine is ready to accept sessions.
    Some reasoning engines take a few seconds to initialize.
    """
    print("Checking engine readiness...")
    start_time = time.time()
    while True:
        try:
            # Attempt to create a session with a short timeout
            session = engine.create_session(user_id=USER_ID)
            engine.delete_session(user_id=USER_ID, session_id=session["id"])
            print("Engine is ready!")
            break
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise RuntimeError(
                    f"Engine did not become ready within {timeout} seconds"
                ) from e
            print("Engine not ready yet, retrying...")
            time.sleep(poll_interval)

# ------------------------------------------
# MAIN
# ------------------------------------------
def main():
    print("Initializing Vertex AI...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("Connecting to Reasoning Engine...")
    engine = agent_engines.get(ENGINE_RESOURCE_ID)

    # Wait until engine is ready to accept sessions
    wait_for_engine_ready(engine)

    print("Creating session...")
    session = engine.create_session(user_id=USER_ID)
    session_id = session["id"]
    print(f"Session created: {session_id}\n")

    print("You can now chat with your Reasoning Engine.")
    print("Type 'quit' to exit.\n")

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower().strip() == "quit":
                break

            # Stream query through the session
            for event in session.stream_query(message=user_input):
                if "content" in event:
                    for part in event["content"].get("parts", []):
                        if "text" in part:
                            print(part["text"], end="", flush=True)
            print("\n")

    finally:
        print("Cleaning up session...")
        engine.delete_session(user_id=USER_ID, session_id=session_id)
        print("Done. Goodbye!")


if __name__ == "__main__":
    main()
