import time
from datetime import timedelta

from cat.utils import verbal_timedelta
from cat.mad_hatter.decorators import hook

@hook(priority=1)
def agent_prompt_chat_history(chat_history, cat):
    history = ""
    tmp = ""
    for turn in chat_history:

        if turn["message"][0:35] != "These are next arrivals at bus stop":
            history += tmp
            tmp = f"\n - {turn['who']}: {turn['message']}"
        else:
            tmp = ""
            
    history += tmp
    
    return history