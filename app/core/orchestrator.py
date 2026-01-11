import os
import json
from typing import Dict, AsyncIterator
from openai import AsyncOpenAI
from dotenv import load_dotenv

from app.core.prompt_builder import build_prompt
from app.config import settings
from app.schemas import LLMResponse


load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def handle_chat(payload: Dict) -> AsyncIterator[str]:

    is_test = payload.get("is_test", False)
    # build prompt based on payload
    prompt = build_prompt(payload)
    print("Generated Prompt:", prompt)

    try:
        # Pydantic 모델을 사용해 JSON Schema 정의
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "llm_response",
                "schema": LLMResponse.model_json_schema(),
                "strict": False
            }
        }

        if is_test:
            # TEST 모드: 전체 응답을 한 번에 생성 (성능 테스트 등 목적)
            completion = await client.chat.completions.create(
                model=settings.model_name,
                messages=prompt,
                response_format=response_format,
                temperature=settings.temperature,
                max_completion_tokens=settings.max_completion_tokens,
                top_p=settings.top_p,
                stream=False
            )
            
            if completion.choices and completion.choices[0].message.content:
                content = completion.choices[0].message.content
                # 전체 내용을 한 번에 전송 (클라이언트 호환성을 위해 포맷 유지)
                yield f"data: {json.dumps(content, ensure_ascii=False)}\n\n"

        else:
            # 기본 모드: 스트리밍 전송
            stream = await client.chat.completions.create(
                model=settings.model_name,
                messages=prompt,
                response_format=response_format,
                temperature=settings.temperature,
                max_completion_tokens=settings.max_completion_tokens,
                top_p=settings.top_p,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # Raw JSON String 조각을 JSON 문자열로 래핑하여 SSE 데이터로 전송
                    # 클라이언트는 event.data를 JSON.parse() 하여 문자열 조각을 얻고 이를 누적해야 함
                    yield f"data: {json.dumps(content, ensure_ascii=False)}\n\n"

        # 스트림 종료 신호
        yield "data: [DONE]\n\n"

    except Exception as e:
        print(f"Streaming Error: {str(e)}")
        # 에러 발생 시 JSON 형태로 에러 정보 전송
        error_payload = json.dumps({"error": str(e)}, ensure_ascii=False)

        yield f"data: {error_payload}\n\n"