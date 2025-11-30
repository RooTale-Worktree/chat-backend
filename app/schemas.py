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

    embedding: Optional[List[float]] = Field(None, description="Vector embeddings for the message")
    embedding_dim: Optional[int] = Field(None, description="Dimension of the vector embeddings")
    embedding_model: Optional[str] = Field(None, description="Model used to generate the embeddings")
    embedding_etag: Optional[str] = Field(None, description="ETag for the embedding model version")
    meta: Optional[Dict] = Field(None, description="Additional metadata for the message")

    def to_dialogue_turn(self) -> DialogueTurn:
        return DialogueTurn(role=self.role, content=self.character_message)
    
class ChatRAGConfig(BaseModel):
    top_k_history: int = Field(5, description="Number of top historical messages to consider")
    history_time_window_min: int = Field(60, description="Time window in minutes for considering historical messages")
    measure: str = Field("cosine", description="Similarity measure to use for embeddings")
    threshold: float = Field(0.75, description="Threshold for similarity to consider a message relevant")
    meta: Optional[Dict] = Field(None, description="Additional metadata for the RAG configuration")

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
    max_new_tokens: int = Field(256, description="Maximum number of new tokens to generate")
    repetition_penalty: float = Field(1.05, description="Repetition penalty for text generation")
    frequency_penalty: float = Field(0.0, description="Frequency penalty for text generation")
    stop: Optional[List[str]] = Field(None, description="List of stop tokens for generation termination")
    reasoning_effort: Literal["low", "medium", "high"] = Field("medium", description="Level of reasoning effort for generation")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's input message for the chat")
    user_name: Optional[str] = Field("User", description="Name of the user")
    persona: Persona = Field(..., description="Persona to use for the chat")
    chat_history: Optional[List[Message]] = Field([], description="List of previous chat messages")
    chat_rag_config: Optional[ChatRAGConfig] = Field(None, description="Configuration for chat retrieval-augmented generation")
    story_title: Optional[str] = Field(None, description="Title of the story context")
    current_story_state: Optional[str] = Field(None, description="Current state or chapter of the story")
    child_story_states: Optional[List[str]] = Field(None, description="List of child story states or chapters") 
    model_cfg: Optional[ModelConfig] = Field(None, description="Configuration for the language model")
    gen: Optional[GenConfig] = Field(None, description="Generation configuration for the language model")
    meta: Optional[Dict] = Field(None, description="Additional metadata for the chat request")


# ========== Schema Definitions for response ==========
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
    narrative: str = Field(..., description="Generated narrative text from the chat")
    character_message: str = Field(..., description="Generated message from the character")
    image_prompt: str = Field(..., description="Prompt for image generation based on the chat")
    next_state_description: Optional[List[UserSelection]] = Field(None, description="Next state or chapter ID for the story")
    embedding: Optional[List[float]] = Field(None, description="Vector embeddings for the generated response")
    usage: Optional[Usage] = Field(None, description="Token usage statistics for the request")
    timing: Optional[Timing] = Field(None, description="Timing information for various stages of the request")


# ========== Schema Definitions for groq request ==========
class GroqResponse(BaseModel):
    narrative: str = Field(..., description="Write in a descriptive, novel-like 3rd person perspective. Focus on the story, scene, and actions.")
    character_message: str = Field(..., description="Write the actual spoken dialogue, strictly adhering to the Speaking Style.")
    image_prompt: str = Field(..., description="A concise English prompt to generate an image describing the current scene.")
    next_state_description: Optional[List[UserSelection]] = Field(None, description="Choices for the user based on [Current Story Context] and [Possible Story Branches]")