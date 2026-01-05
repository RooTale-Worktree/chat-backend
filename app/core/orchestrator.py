import os
from dotenv import load_dotenv
from typing import Dict, AsyncIterator
from openai import AsyncOpenAI

from app.core.prompt_builder import build_prompt
from app.config import settings
from app.schemas import ChatResponse, StreamWrapper, StreamEventType


load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def handle_chat(payload: Dict) -> AsyncIterator[str]:

    # build prompt based on payload
    prompt = build_prompt(payload)
    print("Generated Prompt:", prompt)

    full_text_accumulator = ""

    try:
        stream = await client.chat.completions.create(
            model=settings.model_name,
            messages=prompt,
            stream=True,
            temperature=settings.temperature,
            max_completion_tokens=settings.max_completion_tokens,
            top_p=settings.top_p,
        )

        # Phase 1: delta streaming
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            
            if content:
                full_text_accumulator += content
                
                response_chunk = StreamWrapper(
                    type=StreamEventType.DELTA,
                    content=content
                )
                yield f"data: {response_chunk.model_dump_json()}\n\n"

        # Phase 2: final response
        final_metadata = _calculate_metadata(full_text_accumulator, payload)

        final_response_chunk = StreamWrapper(
            type=StreamEventType.FINAL,
            data=final_metadata
        )
        yield f"data: {final_response_chunk.model_dump_json()}\n\n"

    except Exception as e:
        error_chunk = StreamWrapper(
            type=StreamEventType.ERROR,
            data=ChatResponse(
                next_node_id="", text_output=[], image_prompt="", next_choice_description=[],
                error=str(e)
            )
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"

    # 스트림 종료 신호
    yield "data: [DONE]\n\n"


def _calculate_metadata(full_text: str, payload: Dict) -> ChatResponse:
    """
    완성된 텍스트를 바탕으로 나머지 필드(next_node_id, image_prompt 등)를 결정하는 로직
    """
    # TODO: 여기에 실제 비즈니스 로직을 구현하세요.
    # 예: 룰베이스로 다음 노드를 찾거나, 텍스트 분석을 위해 LLM을 한 번 더 호출하거나 등등.
    
    return ChatResponse(
        next_node_id="calculated_next_node_123",  # 로직 결과
        text_output=[{"role": "assistant", "content": full_text}],
        image_prompt=f"A fantasy scene description based on: {full_text[:30]}...",
        next_choice_description=["Go North", "Stay here"]
    )