from __future__ import annotations
import os
import time
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Iterator

from app.core.prompt_builder import build_prompt
from app.core.story_retriever import retrieve_story_context
from app.schemas import GroqResponse

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def handle_chat(payload: Dict) -> Iterator[str]:
    """
    Handle a single chat turn with streaming.    
    Args:
        payload: ChatRequest dict
    Returns:
        Iterator[str]: SSE formatted chunks
    """
    # timing = {} # Timing is less relevant in streaming
    # start_time = time.time()

    # Parse payload
    message = payload.get("message", "")
    user_name = payload.get("user_name", "User")
    persona = payload.get("persona", None)
    chat_history = payload.get("chat_history", [])
    story_title = payload.get("story_title", None)
    story = payload.get("story", None)
    model_config = payload.get("model_cfg") or {}
    gen = payload.get("gen") or {}
    meta = payload.get("meta", {})

    chat_context = chat_history
    story_context = []
    if story_title or story:
        # tmp_time = time.time()
        story_context = retrieve_story_context(
            story_title=story_title,
            user_query=message,
            story=story
        )
        # timing["story_retr_ms"] = int((time.time() - tmp_time) * 1000)
    print(f"\n[System] story_context: {story_context}")
    
    prompt_input = {
        "persona": persona,
        "user_name": user_name,
        "chat_context": chat_context,
        "story_context": story_context,
        "user_message": message,
        "reasoning_effort": gen.get("reasoning_effort", "low"),
    }
    prompt = build_prompt(prompt_input)
    print(f"\n[System] prompt: {prompt}\n")

    # API Call
    client = Groq()
    stream = client.chat.completions.create(
        model=model_config.get("model_name", "openai/gpt-oss-20b"),
        messages=prompt,
        # response_format={"type": "json_object"}, # Disable strict JSON mode for true streaming
        # reasoning_effort=gen.get("reasoning_effort", "low"),
        temperature=gen.get("temperature", 0.5),
        top_p=gen.get("top_p", 0.9),
        max_completion_tokens=gen.get("max_new_tokens", 1024),
        frequency_penalty=gen.get("frequency_penalty", 0),
        stream=True
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            # Yield raw content delta for true streaming effect
            # Client must handle partial JSON parsing if needed
            yield f"data: {content}\n\n"
