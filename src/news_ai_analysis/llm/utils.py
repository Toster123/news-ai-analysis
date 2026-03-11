from typing import Dict


def extract_content(message: str | Dict, remove_think_tags: bool = True):
    if type(message) != "str":
        message = message.content
    if remove_think_tags:
        return message.replace("<think>", "").split("</think>")[-1]
    return message