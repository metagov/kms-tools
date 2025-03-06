from koi import llm

def conversation(message):
    thread_id = message.get("thread_ts")
    message_id = message.get("ts")

    conversation_id = thread_id or message_id

    return llm.continue_conversation(conversation_id, message["text"])