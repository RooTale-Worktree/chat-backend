from __future__ import annotations
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


# ========================= LLM 응답 스키마 =========================
class LLMResponse(BaseModel):
    text_output: List[TextOutputItem] = Field(..., description=(
        "A sequence of 8~12 items "
        "mixing narrative and character_message. "
        "This sequence must logically bridge the user's input to the consequence, "
        "effectively advancing the plot within the current scene context."
    ))
    next_node_id: str = Field(..., description=(
        "The CRITICAL decision for story progression. "
        "Analyze the 'Transition Logic' in the prompt. "
        "If the user's input/action meets a specific Candidate condition, "
        "this MUST be that Candidate's ID. "
        "If no condition is met, return the current node ID."
    ))
    image_prompt: str = Field(..., description=(
        "A detailed description of the final visual scene in ENGLISH. "
        "Focus on visual elements: lighting, camera angle, character appearance, background texture, and mood. "
        "Do not include dialogue or abstract concepts."
    ))
    next_choice_description: List[str] = Field(..., description=(
        "A list of 2~4 short, actionable choices for the user's next turn. "
        "These choices should be natural continuations of the current situation and may hint at future branching paths."
    ))

class TextOutputItem(BaseModel):
    type: Literal["narrative", "character_message"] = Field("narrative", description=(
        "Strictly classifies the content. "
        "Use 'narrative' for scene descriptions, actions, and atmosphere. "
        "Use 'character_message' ONLY for spoken dialogue by characters."
    ))
    speaker: Optional[str] = Field(None, description=(
        "The exact name of the character speaking. "
        "MUST be provided if type is 'character_message'. MUST be None (null) if type is 'narrative'. "
        "The name must match one of the 'Active Characters' in the context."
    ))
    text: str = Field(..., description=(
        "The actual content text. "
        "If type is 'narrative', describe the scene objectively or sensory details. "
        "If type is 'character_message', write only the spoken lines without quotes or internal thoughts."
    ))