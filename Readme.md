# Character Chat Generation API

캐릭터/스토리 기반 대화 생성과 장면 진행을 위한 FastAPI 백엔드 서버입니다. 요청된 세계관(universe), 현재 장면(scene), 후보 분기(candidates)를 바탕으로 구조화된 JSON 응답을 생성하며, 기본적으로 SSE 스트리밍으로 전송합니다.

## 기능

- Universe/Scene/Candidate 기반 스토리 대화 생성
- JSON Schema 기반 구조화된 출력 (narrative / character_message 분리)
- SSE(text/event-stream) 스트리밍 응답
- 이미지 생성 프롬프트 생성
- OpenAI API(AsyncOpenAI) 연동
- loop_count 기반 장면 전환 로직

## 로컬 테스트 실행 방법

### 1. 환경 설정

**Python 버전**: 3.11 이상 권장

**의존성 설치**:
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here

# 선택: 기본값을 덮어쓰고 싶을 때만 설정
MODEL_NAME=gpt-5.1-chat-latest
TEMPERATURE=1.0
MAX_COMPLETION_TOKENS=4096
TOP_P=1.0
```

### 3. 서버 실행

```bash
# 개발 모드로 실행 (자동 재시작 활성화)
python -m app.main

# 또는 uvicorn 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면 다음 URL에서 접근 가능합니다:
- API 서버: `http://localhost:8000`
- Health Check: `http://localhost:8000/health`
- API 문서 (Swagger): `http://localhost:8000/docs`

### 4. Docker를 사용한 실행 (선택사항)

```bash
# 이미지 빌드
docker build -t chat-backend .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env chat-backend
```

## API 명세

### POST `/v1/chat`

세계관/씬/후보 정보를 기반으로 다음 장면을 생성합니다. 기본 응답은 SSE 스트리밍(`text/event-stream`)입니다.

#### Request Body

```json
{
  "user_message": "string (필수)",
  "loop_count": 0,
  "chat_history": [
    {
      "role": "user | assistant",
      "type": "narrative | character_message",
      "text": "string",
      "speaker": "string | null"
    }
  ],
  "universe": {
    "protagonist": "string (필수)",
    "protagonist_desc": "string (필수)",
    "setting": "string (필수)"
  },
  "scene": {
    "node_id": "string (필수)",
    "characters": ["string"] (필수),
    "description": "string (필수)"
  },
  "candidates": [
    {
      "candidate_id": "string (필수)",
      "condition": "string (필수)"
    }
  ],
  "is_test": false
}
```

#### Request 필드 설명

**기본 필드**
- `user_message`: 사용자 입력 메시지
- `loop_count`: 현재 scene에서 머문 횟수 (전환 로직에 사용)
- `is_test`: `true`일 때 스트리밍 대신 단일 응답으로 전송 (SSE 포맷은 유지)

**chat_history**
- `role`: `"user"` 또는 `"assistant"`
- `type`: `"narrative"` 또는 `"character_message"`
- `text`: 대화 내용
- `speaker`: `character_message`일 때만 캐릭터 이름을 지정 (narrative는 `null`)

**universe**
- `protagonist`: 주인공 이름
- `protagonist_desc`: 주인공 설명
- `setting`: 세계관/배경 설정

**scene**
- `node_id`: 현재 scene 노드 ID
- `characters`: 현재 scene에 등장하는 캐릭터 목록
- `description`: scene 설명

**candidates**
- `candidate_id`: 다음 후보 노드 ID
- `condition`: 해당 노드로 전환되는 조건 설명

#### Response (SSE 스트리밍)

- `Content-Type: text/event-stream`
- 각 `data:` 이벤트는 **JSON 문자열 조각**입니다.
- 모든 조각을 이어 붙인 뒤 JSON으로 파싱하면 최종 응답 객체를 얻습니다.
- 스트림 종료 시 `data: [DONE]` 이벤트가 전송됩니다.

**최종 응답 JSON 구조**

```json
{
  "text_output": [
    {
      "role": "assistant",
      "type": "narrative",
      "text": "string",
      "speaker": null
    },
    {
      "role": "assistant",
      "type": "character_message",
      "text": "string",
      "speaker": "string"
    }
  ],
  "next_node_id": "string",
  "image_prompt": "string",
  "next_choice_description": ["string"]
}
```

#### 예시 요청

```bash
curl -N -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d @test/example.json
```

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── config.py                # 환경 설정 (모델/샘플링)
│   ├── schemas.py               # Pydantic 모델 정의
│   ├── core/
│   │   ├── orchestrator.py      # LLM 호출 및 SSE 스트리밍
│   │   └── prompt_builder.py    # 프롬프트 생성
│   ├── routers/
│   │   ├── chat.py              # 채팅 엔드포인트
│   │   └── story.py             # (현재 placeholder)
│   └── story_indexes/           # 스토리 인덱스 파일들
│       ├── downwater/
│       ├── sonoris/
│       └── verdia/
├── test/
│   ├── example.json             # 요청 예시
│   └── risu_prompt.json         # 프롬프트 샘플
├── requirements.txt
├── Dockerfile
├── vercel.json
└── Readme.md
```