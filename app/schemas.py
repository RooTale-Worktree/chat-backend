from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# ========================= 요청 스키마 =========================
class ChatRequest(BaseModel):
    user_message: str = Field(..., description="사용자가 입력한 메시지")
    loop_count: int = Field(0, description="사용자가 현재 scene 노드에서 머문 횟수")
    chat_history: List[ChatItem] = Field([], description="사용자의 이전 대화 내역")
    universe: UniverseItem = Field(..., description="현재 universe의 주인공과 배경 정보")
    scene: SceneItem = Field(..., description="현재 scene 노드의 세부 정보")
    candidates: List[CandidateItem] = Field([], description="현재 scene 노드의 자식 노드 목록")
    is_test: bool = Field(False, description="개발 과정에서 테스트용 플래그")

class ChatItem(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="대화 생성 주체")
    type: Literal["narrative", "character_message"] = Field(..., description="대화 항목의 유형")
    text: str = Field(..., description="대화 내용")
    speaker: Optional[str] = Field(None, description="발화자 이름 (character_message 타입일 때만 해당)")

class UniverseItem(BaseModel):
    protagonist: str = Field(..., description="현재 universe의 주인공 캐릭터 이름")
    protagonist_desc: str = Field(..., description="주인공 캐릭터에 대한 설명")
    setting: str = Field(..., description="현재 universe의 배경 설정")

class SceneItem(BaseModel):
    node_id: str = Field(..., description="scene 노드의 ID")
    characters: List[str] = Field(..., description="scene에 등장하는 캐릭터 목록")
    description: str = Field(..., description="scene 노드에 대한 설명")

class CandidateItem(BaseModel):
    candidate_id: str = Field(..., description="후보 노드의 ID")
    condition: str = Field(..., description="해당 후보 노드로 전환되기 위한 조건 설명")


# ========================= 응답 스키마 =========================
class ChatResponse(BaseModel):
    text_output: List[ChatItem] = Field(None, description="생성된 대화 출력 항목 목록") 
    next_node_id: str = Field(..., description="다음에 전환될 scene 노드의 ID")
    image_prompt: str = Field(..., description="이미지 생성 프롬프트")
    next_choice_description: List[str] = Field(..., description="다음 선택지 목록")
    error: Optional[str] = Field(None, description="오류 메시지")