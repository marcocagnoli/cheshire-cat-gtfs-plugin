import time
from datetime import timedelta

from cat.utils import verbal_timedelta
from cat.mad_hatter.decorators import hook

@hook(priority=1)
def agent_prompt_chat_history(chat_history, cat):
    history = ""
    tmp = ""
    who = ""
    message = ""
    for turn in chat_history:

        if turn["message"][0:35] != "These are next arrivals at bus stop":
            history += tmp
            tmp = f"\n - {turn['who']}: {turn['message']}"
            message = turn["message"]
            who = turn["who"]
        else:
            tmp = ""
    
    if history != "" and (' '.join(message.split())  == "In order to give you these information, I need three configuration parameters. I need to save Api Key. Which is Tranit Land Api Key?" or message == "I need to save Transit Land OneStopID. Which is Transit Land OneStopID?" or message == "I need to save GTFS TimeZone. Which is GTFS TimeZone?"):
        history = f"\n - {who}: {message}"
    else:    
        history += tmp
        
    return history

@hook(priority=1)
def agent_prompt_episodic_memories(memory_docs, cat):
    # convert docs to simple text
    memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

    # add time information (e.g. "2 days ago")
    memory_timestamps = []
    for m in memory_docs:
        timestamp = m[0].metadata["when"]
        delta = timedelta(seconds=(time.time() - timestamp))
        memory_timestamps.append(f" ({verbal_timedelta(delta)})")

    memory_texts = [a + b for a, b in zip(memory_texts, memory_timestamps)]

    memories_separator = "\n  - "
    memory_content = memories_separator + memories_separator.join(memory_texts)

    f = open("./cat/plugins/gtfs/memory.txt", "a")
    f.write(memory_content)
    f.close()
    
    memory_content = "\n"
    
    return memory_content

@hook(priority=1)
def agent_prompt_declarative_memories(memory_docs, cat):
    # convert docs to simple text
    memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

    # add source information (e.g. "extracted from file.txt")
    memory_sources = []
    for m in memory_docs:
        source = m[0].metadata["source"]
        memory_sources.append(f" (extracted from {source})")

    memory_texts = [a + b for a, b in zip(memory_texts, memory_sources)]

    memories_separator = "\n  - "
    memory_content = memories_separator + memories_separator.join(memory_texts)

    memory_content = "\n"

    return memory_content

@hook(priority=1)
def agent_prompt_suffix(cat):
    suffix = """Conversation until now:{chat_history}
 - Human: {input}

{agent_scratchpad}"""
    return suffix