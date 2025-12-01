# Character Chat Generation API

캐릭터 기반 대화 생성 및 인터랙티브 스토리 진행을 위한 FastAPI 기반 백엔드 서버입니다.

## 기능

- 캐릭터 페르소나 기반 대화 생성
- 인터랙티브 스토리 분기 및 진행
- 대화 히스토리 관리
- 이미지 생성 프롬프트 자동 생성
- Groq API를 통한 LLM 추론

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
GROQ_API_KEY=your_groq_api_key_here
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

캐릭터와의 대화를 생성하고 스토리를 진행하는 엔드포인트입니다.

#### Request Body

```json
{
  "message": "string (필수)",
  "user_name": "string (선택, 기본값: User)",
  "persona": {
    "character_name": "string (필수)",
    "persona": "string (필수)",
    "scenario": "string (필수)",
    "speaking_style": ["string"] (필수),
    "example_dialogue": [
      {
        "role": "string (필수)",
        "content": "string (필수)"
      }
    ] (필수),
    "meta": {} (선택)
  },
  "chat_history": [
    {
      "narrative": "string (선택)",
      "character_message": "string (필수)",
      "role": "string (필수)",
      "embedding": [float] (선택),
      "embedding_dim": int (선택),
      "embedding_model": "string (선택)",
      "embedding_etag": "string (선택)",
      "meta": {} (선택)
    }
  ] (선택, 기본값: []),
  "chat_rag_config": {
    "top_k_history": int (선택, 기본값: 5),
    "history_time_window_min": int (선택, 기본값: 60),
    "measure": "string (선택, 기본값: cosine)",
    "threshold": float (선택, 기본값: 0.75),
    "meta": {} (선택)
  } (선택),
  "story_title": "string (선택)",
  "current_story_state": "string (선택)",
  "child_story_states": ["string"] (선택),
  "model_cfg": {
    "model_name": "string (선택, 기본값: openai/gpt-oss-20b)",
    "tensor_parallel_size": int (선택, 기본값: 1),
    "gpu_memory_utilization": float (선택, 기본값: 0.9),
    "max_model_length": int (선택, 기본값: 131072),
    "max_num_seqs": int (선택, 기본값: 8),
    "trust_remote_code": bool (선택, 기본값: true),
    "dtype": "string (선택, 기본값: auto)"
  } (선택),
  "gen": {
    "temperature": float (선택, 기본값: 0.5),
    "top_p": float (선택, 기본값: 0.9),
    "max_new_tokens": int (선택, 기본값: 256),
    "repetition_penalty": float (선택, 기본값: 1.05),
    "frequency_penalty": float (선택, 기본값: 0.0),
    "stop": ["string"] (선택),
    "reasoning_effort": "low | medium | high (선택, 기본값: medium)"
  } (선택),
  "meta": {} (선택)
}
```

#### Request 필드 설명

**기본 필드**
- `message`: 사용자의 입력 메시지
- `user_name`: 사용자 이름

**persona** (캐릭터 설정)
- `character_name`: 캐릭터의 이름
- `persona`: 캐릭터의 성격과 배경 설명
- `scenario`: 현재 시나리오 또는 상황 설명
- `speaking_style`: 캐릭터의 말투 특징 리스트
- `example_dialogue`: 캐릭터의 대화 예시 (few-shot learning용)
  - `role`: 화자 역할 (`"user"` 또는 `"assistant"`)
  - `content`: 대화 내용
- `meta`: 추가 메타데이터

**chat_history** (대화 히스토리)
- `narrative`: 서사 텍스트 (3인칭 시점 묘사)
- `character_message`: 캐릭터의 메시지
- `role`: 메시지 발신자 역할 (`"user"` 또는 `"assistant"`)
- `embedding`: 메시지의 벡터 임베딩
- `embedding_dim`: 임베딩 차원
- `embedding_model`: 임베딩 생성에 사용된 모델
- `embedding_etag`: 임베딩 모델 버전 태그
- `meta`: 추가 메타데이터

**chat_rag_config** (RAG 설정)
- `top_k_history`: 검색할 과거 메시지 개수
- `history_time_window_min`: 고려할 과거 메시지 시간 범위 (분)
- `measure`: 유사도 측정 방법 (기본: cosine)
- `threshold`: 관련 메시지로 판단할 유사도 임계값

**스토리 관련 필드**
- `story_title`: 스토리 제목 (스토리 컨텍스트 검색용)
- `current_story_state`: 현재 스토리 상태/노드 ID
- `child_story_states`: 가능한 다음 스토리 상태 ID 리스트

**model_cfg** (모델 설정)
- `model_name`: 사용할 LLM 모델명
- `tensor_parallel_size`: 텐서 병렬 처리 크기
- `gpu_memory_utilization`: GPU 메모리 사용률
- `max_model_length`: 최대 모델 입력 길이
- `max_num_seqs`: 병렬 처리할 최대 시퀀스 수
- `trust_remote_code`: 원격 코드 실행 신뢰 여부
- `dtype`: 모델 가중치 데이터 타입

**gen** (생성 설정)
- `temperature`: 샘플링 온도 (높을수록 창의적, 낮을수록 결정적)
- `top_p`: Nucleus 샘플링 파라미터
- `max_new_tokens`: 생성할 최대 토큰 수
- `repetition_penalty`: 반복 억제 페널티
- `frequency_penalty`: 빈도 기반 페널티
- `stop`: 생성 중단 토큰 리스트
- `reasoning_effort`: 추론 수준 (`"low"`, `"medium"`, `"high"`)

#### Response Body

```json
{
  "narrative": "string (필수)",
  "character_message": "string (필수)",
  "image_prompt": "string (필수)",
  "next_state_description": [
    {
      "next_state_id": "string (필수)",
      "choice_description": "string (필수)"
    }
  ] (선택),
  "embedding": [float] (선택),
  "usage": {
    "prompt_tokens": int (필수),
    "completion_tokens": int (필수),
    "total_tokens": int (필수),
    "finish_reason": "string (필수)"
  } (선택),
  "timing": {
    "message_embed_ms": int (선택),
    "chat_retr_ms": int (선택),
    "story_retr_ms": int (선택),
    "llm_load_ms": int (선택),
    "generate_ms": int (선택),
    "response_embed_ms": int (선택),
    "total_ms": int (선택)
  } (선택)
}
```

#### Response 필드 설명

**생성 결과**
- `narrative`: 생성된 서사 텍스트 (3인칭 시점 묘사, 장면과 행동에 집중)
- `character_message`: 캐릭터의 대사 (캐릭터의 말투 스타일 반영)
- `image_prompt`: 현재 장면을 묘사하는 이미지 생성 프롬프트 (영어)

**스토리 분기**
- `next_state_description`: 다음 가능한 스토리 분기 리스트
  - `next_state_id`: 스토리 분기의 노드 ID
  - `choice_description`: 해당 분기에 대한 간단한 설명 (예: "그에게 이유를 묻는다", "검을 뽑는다")

**메타데이터**
- `embedding`: 응답의 벡터 임베딩 (향후 RAG 검색용)
- `usage`: 토큰 사용량 통계
  - `prompt_tokens`: 프롬프트에 사용된 토큰 수
  - `completion_tokens`: 생성된 토큰 수
  - `total_tokens`: 총 토큰 수
  - `finish_reason`: 생성 종료 이유
- `timing`: 각 단계별 처리 시간 (밀리초)
  - `message_embed_ms`: 메시지 임베딩 생성 시간
  - `chat_retr_ms`: 대화 히스토리 검색 시간
  - `story_retr_ms`: 스토리 컨텍스트 검색 시간
  - `llm_load_ms`: LLM 모델 로딩 시간
  - `generate_ms`: 텍스트 생성 시간
  - `response_embed_ms`: 응답 임베딩 생성 시간
  - `total_ms`: 전체 처리 시간

#### 예시 요청

```bash
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요?",
    "user_name": "사용자",
    "persona": {
      "character_name": "엘리제",
      "persona": "냉정하고 이성적인 마법사. 과거의 상처로 인해 타인과 거리를 두지만, 내면에는 따뜻한 마음을 지니고 있다.",
      "scenario": "심해 도시에서 위험한 음모를 조사 중이다.",
      "speaking_style": [
        "간결하고 명료한 말투",
        "감정을 드러내지 않는 차분한 어조",
        "필요한 말만 하는 경향"
      ],
      "example_dialogue": [
        {
          "role": "user",
          "content": "같이 가도 될까요?"
        },
        {
          "role": "assistant",
          "content": "...좋아. 하지만 방해는 하지 마."
        }
      ]
    },
    "gen": {
      "temperature": 0.7,
      "max_new_tokens": 300,
      "reasoning_effort": "medium"
    }
  }'
```

#### 예시 응답

```json
{
  "narrative": "엘리제는 차갑게 빛나는 푸른 눈으로 당신을 바라보았다. 그녀의 표정은 여전히 무표정했지만, 잠시 망설이는 듯한 기색이 스쳤다.",
  "character_message": "...누구지? 이곳에 함부로 들어올 수 있는 사람은 없는데.",
  "image_prompt": "A mysterious female mage with cold blue eyes and silver hair, standing in a dimly lit underwater city, magical blue light illuminating her face",
  "next_state_description": [
    {
      "next_state_id": "node_123_1",
      "choice_description": "자신을 소개하고 협력을 제안한다"
    },
    {
      "next_state_id": "node_123_2",
      "choice_description": "조심스럽게 물러난다"
    }
  ],
  "usage": {
    "prompt_tokens": 450,
    "completion_tokens": 120,
    "total_tokens": 570,
    "finish_reason": "stop"
  },
  "timing": {
    "generate_ms": 1250,
    "total_ms": 1320
  }
}
```

## 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── schemas.py               # Pydantic 모델 정의
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # 메인 로직 조율
│   │   ├── prompt_builder.py    # 프롬프트 생성
│   │   └── story_retriever.py   # 스토리 컨텍스트 검색
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py              # 채팅 엔드포인트
│   └── story_indexes/           # 스토리 인덱스 파일들
│       └── downwater/           # 예: 심해의 공명 도시
│           ├── docstore.json
│           ├── index_store.json
│           └── story_info.json
├── requirements.txt
├── Dockerfile
└── Readme.md
```

## 기술 스택

- **FastAPI**: 고성능 웹 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **Groq API**: LLM 추론 및 구조화된 출력
- **LlamaIndex**: 스토리 인덱스 관리 (선택사항)
- **Sentence Transformers**: 한국어 텍스트 임베딩 (선택사항, ko-sbert-nli)
- **PyTorch**: 딥러닝 프레임워크 (임베딩 모델용)

## 라이선스

MIT License