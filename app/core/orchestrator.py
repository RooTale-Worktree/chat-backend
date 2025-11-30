from __future__ import annotations
import os
import time
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Dict

from app.core.prompt_builder import build_prompt
# from app.core.story_retriever import retrieve_story_context
from app.schemas import GroqResponse

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def handle_chat(payload: Dict) -> Dict:
    """
    Handle a single chat turn.    
    Args:
        payload: ChatRequest dict
    Returns:
        ChatResponse: dict
    """
    timing = {}
    start_time = time.time()

    # Parse payload
    message = payload.get("message", "")
    user_name = payload.get("user_name", "User")
    persona = payload.get("persona", None)
    chat_history = payload.get("chat_history", [])
    chat_rag_config = payload.get("chat_rag_config", {})
    story_title = payload.get("story_title", None)
    model_config = payload.get("model_cfg", {})
    gen = payload.get("gen", {})
    meta = payload.get("meta", {})

    chat_context = chat_history

    story_context = []
    # if story_title:
    #     tmp_time = time.time()
    #     story_context = retrieve_story_context(
    #         story_title=story_title,
    #         user_query=message
    #     )
    #     timing["story_retr_ms"] = int((time.time() - tmp_time) * 1000)
    
    prompt_input = {
        "persona": persona,
        "user_name": user_name,
        "chat_context": chat_context,
        "story_context": story_context,
        "user_message": message,
        "reasoning_effort": gen.get("reasoning_effort", "low"),
    }
    prompt = build_prompt(prompt_input)

    # API Call
    tmp_time = time.time()
    client = Groq()
    response = client.chat.completions.create(
        model=model_config.get("model_name", "openai/gpt-oss-20b"),
        messages=prompt,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ChatResponse",
                "schema": GroqResponse.model_json_schema(),
            }
        },
        reasoning_effort=gen.get("reasoning_effort", "low"),
        temperature=gen.get("temperature", 0.5),
        top_p=gen.get("top_p", 0.9),
        max_completion_tokens=gen.get("max_new_tokens", 256),
        frequency_penalty=gen.get("frequency_penalty", 0),
    )
    timing["generate_ms"] = int((time.time() - tmp_time) * 1000)

    timing["total_ms"] = int((time.time() - start_time) * 1000)

    # Parse response
    content_str = response.choices[0].message.content
    parsed_data = json.loads(content_str)

    # Usage info
    response_usage = response.usage
    usage = {
        "prompt_tokens": response_usage.prompt_tokens,
        "completion_tokens": response_usage.completion_tokens,
        "total_tokens": response_usage.total_tokens,
        "finish_reason": response.choices[0].finish_reason,
    }

    return {
        "narrative": parsed_data.get("narrative", ""),
        "character_message": parsed_data.get("character_message", ""),
        "image_prompt": parsed_data.get("image_prompt", ""),
        "usage": usage,
        "timing": timing,
    }
