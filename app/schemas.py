from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime


# ========== Schema Definitions for request ==========
class DialogueTurn(BaseModel):
    role: str = Field(..., description="Role of the speaker in the dialogue (e.g., user, assistant)")
    content: str = Field(..., description="Content of the dialogue turn")

class Persona(BaseModel):
    character_name: str = Field(..., description="Name of the character")
    persona: str = Field(..., description="Persona description of the character")
    scenario: str = Field(..., description="Scenario in which the character operates")
    speaking_style: List[str] = Field(..., description="List of speaking style attributes")
    example_dialogue: List[DialogueTurn] = Field(..., description="Example dialogues for the character")
    meta: Optional[Dict] = Field(None, description="Additional metadata for the persona")

class Message(BaseModel):
    narrative: Optional[str] = Field(None, description="Narrative text associated with the message")
    character_message: str = Field(..., description="Message from the character")
    role: str = Field(..., description="Role of the message sender (e.g., user, assistant)")
    def to_dialogue_turn(self) -> DialogueTurn:
        return DialogueTurn(role=self.role, content=self.character_message)

class ModelConfig(BaseModel):
    model_name: str = Field("openai/gpt-oss-20b", description="Name of the language model to use")
    tensor_parallel_size: int = Field(1, description="Size of tensor parallelism for model inference")
    gpu_memory_utilization: float = Field(0.9, description="Fraction of GPU memory to utilize for model inference")
    max_model_length: int = Field(131_072, description="Maximum length of the model input")
    max_num_seqs: int = Field(8, description="Maximum number of sequences to process in parallel")
    trust_remote_code: bool = Field(True, description="Whether to trust remote code execution for model loading")
    dtype: str = Field("auto", description="Data type for model weights (e.g., fp16, bf16)")

class GenConfig(BaseModel):
    temperature: float = Field(0.5, description="Sampling temperature for text generation")
    top_p: float = Field(0.9, description="Top-p (nucleus) sampling parameter")
    max_new_tokens: int = Field(1024, description="Maximum number of new tokens to generate")
    repetition_penalty: float = Field(1.05, description="Repetition penalty for text generation")
    frequency_penalty: float = Field(0.0, description="Frequency penalty for text generation")
    stop: Optional[List[str]] = Field(None, description="List of stop tokens for generation termination")
    reasoning_effort: Literal["low", "medium", "high"] = Field("low", description="Level of reasoning effort for generation")

class CurrentStoryState(BaseModel):
    node_id: str = Field(..., description="ID of the current story state node")
    node_name: str = Field(..., description="Name of the current story state node")
    description: str = Field(..., description="Description of the current story state")
    loop_count: int = Field(0, description="Number of times the user has looped back to this state")
    max_loop_before_branch: int = Field(3, description="Maximum loops allowed before forcing a story branch")

class ChildStoryState(BaseModel):
    node_id: str = Field(..., description="ID of the child story state node")
    summary: str = Field(..., description="Summary of the child story state")
    conditions: List[str] = Field(..., description="Conditions required to access this child story state")

class Story(BaseModel):
    current_story_state: CurrentStoryState = Field(..., description="Current state of the story")
    child_story_states: List[ChildStoryState] = Field(..., description="List of possible child states from the current story state")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's input message for the chat")
    user_name: Optional[str] = Field("User", description="Name of the user")
    persona: Persona = Field(..., description="Persona to use for the chat")
    chat_history: Optional[List[Message]] = Field([], description="List of previous chat messages")
    story_title: Optional[str] = Field(None, description="Title of the story context")
    story: Optional[Story] = Field(None, description="Story context including current and child states")
    model_cfg: Optional[ModelConfig] = Field(None, description="Configuration for the language model")
    gen: Optional[GenConfig] = Field(None, description="Generation configuration for the language model")
    meta: Optional[Dict] = Field(None, description="Additional metadata for the chat request")


# ========== Schema Definitions for response ==========
class Dialogue(BaseModel):
    narrative: str = Field(..., description="Narrative text of the dialogue")
    character_message: str = Field(..., description="Message from the character")

class Usage(BaseModel):
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total number of tokens used")
    finish_reason: str = Field(..., description="Reason for finishing the generation")

class UserSelection(BaseModel):
    next_state_id: str = Field(..., description="The ID from the story branch.")
    choice_description: str = Field(..., description="A short, immersive text describing the user's action or dialogue option corresponding to that branch (e.g., \"Ask him why.\", \"Draw your sword.\")")

class Timing(BaseModel):
    message_embed_ms: Optional[int] = Field(None, description="Time taken to compute message embeddings in milliseconds")
    chat_retr_ms: Optional[int] = Field(None, description="Time taken for chat retrieval in milliseconds")
    story_retr_ms: Optional[int] = Field(None, description="Time taken for story retrieval in milliseconds")
    llm_load_ms: Optional[int] = Field(None, description="Time taken to load the language model in milliseconds")
    generate_ms: Optional[int] = Field(None, description="Time taken for text generation in milliseconds")
    response_embed_ms: Optional[int] = Field(None, description="Time taken to compute response embeddings in milliseconds")
    total_ms: Optional[int] = Field(None, description="Total time taken for the request in milliseconds")

class ChatResponse(BaseModel):
    dialogues:List[Dialogue] = Field(..., description="List of dialogues generated in response to the chat")
    image_prompt: str = Field(..., description="Prompt for image generation based on the chat")
    user_choices: Optional[List[UserSelection]] = Field(None, description="Next state or chapter ID for the story")
    current_state: str = Field(..., description="Current state description after the chat")

# ========== Schema Definitions for groq request ==========
class GroqResponse(BaseModel):
    narrative: str = Field(..., description="Write in a descriptive, novel-like 3rd person perspective. Focus on the story, scene, and actions.")
    character_message: str = Field(..., description="Write the actual spoken dialogue, strictly adhering to the Speaking Style.")
    image_prompt: str = Field(..., description="A concise English prompt to generate an image describing the current scene.")
    next_state_description: Optional[List[UserSelection]] = Field(None, description="Choices for the user based on [Current Story Context] and [Possible Story Branches]")