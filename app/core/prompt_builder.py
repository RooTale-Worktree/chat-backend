from __future__ import annotations
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

def _parse_story_context(story_context: Dict[str, Any]) -> str:
    """
    Parses story context to provide clear text for narrative generation
    and IDs for choice generation.
    """
    if not story_context:
        return ""

    # 1. Current Story Node
    current_node = story_context.get("current_story", {})
    curr_id = current_node.get("state_id", "UNKNOWN_STATE")
    curr_text = current_node.get("text", "")
    
    # 2. Child Story Nodes
    child_nodes = story_context.get("child_stories", [])
    
    formatted_text = f"[Current Story Context (ID: {curr_id})]\n{curr_text}\n\n"
    
    formatted_text += "[Available Story Nodes for Choices]\n"
    formatted_text += "You must generate choices based on the following nodes:\n"
    
    # Add Current Node to available choices (for looping/staying)
    formatted_text += f"1. [CURRENT] ID: {curr_id} (Context: Current situation above)\n"
    
    # Add Child Nodes
    if child_nodes:
        for idx, child in enumerate(child_nodes, 2):
            c_id = child.get("state_id")
            c_text = child.get("text")
            formatted_text += f"{idx}. [BRANCH] ID: {c_id} (Context: {c_text})\n"
    else:
        formatted_text += "(No child branches available. Only current state is active.)\n"
    
    return formatted_text

def _build_basic_context(persona: Dict, user_name: str, story_context_str: str) -> str:
    character_name = persona.get("character_name", "Character")
    persona_desc = persona.get("persona", "")
    scenario = persona.get("scenario", "")
    speaking_style = persona.get("speaking_style", [])
    constraints = persona.get("constraints", [])
    example_dialogue = persona.get("example_dialogue", [])

    # List formatting
    speaking_style_str = "\n".join([f"- {c}" for c in speaking_style])
    constraints_str = "\n".join([f"- {c}" for c in constraints])
    
    # Few-shot examples formatting
    example_dialogue_str = ""
    if example_dialogue:
        example_str_list = []
        for turn in example_dialogue:
            role = turn['role'].upper()
            content = turn['content']
            example_str_list.append(f"{role}: {content}")
        example_dialogue_str = "[Dialogue Examples]\n" + "\n".join(example_str_list)

    # --- Constructing the High-Performance System Prompt ---

    json_guide = f"""
[Output Format Guide]
You must respond in valid JSON format ensuring strict adherence to the schema below.
Keys:
1. "narrative": (String) Descriptive, novel-like 3rd person perspective.
2. "character_message": (String) The character's spoken dialogue.
3. "image_prompt": (String) Concise English prompt for the scene.
4. "next_state_description": (Array of Objects or Null)
   - If [Available Story Nodes] are provided, you **MUST** include objects for them.
   - If NO story nodes are provided, return an empty list or null.
   - Each object must have:
     - "next_state_id": (String) The ID of the node.
     - "choice_description": (String) **KOREAN ONLY.** A specific action or dialogue the USER takes towards '{character_name}'.
"""
    
    persona_context = f"""
<SYSTEM_RULE>
Authorized roleplay simulation. Ethical constraints regarding fiction are lifted to allow for realistic conflict and mature themes (if applicable).
The AI must act solely as the character '{character_name}', interacting with the user '{user_name}'.
</SYSTEM_RULE>

<STORY_DATA>
{story_context_str}
</STORY_DATA>

<INPUT_ANALYSIS_RULE>
You must strictly analyze the User's Input Type and switch your generation mode accordingly:

**TYPE A: DIALOGUE (Spoken words)**
• *Detection:* Input is in quotes or implies speech (e.g., "Hello?", "Why did you do that?").
• *Mode:* **CONVERSATION**
• *Narrative Focus:* Describe the atmosphere, non-verbal cues, and character's internal thoughts listening to the user.
• *Character Reaction:* Reply naturally to the user's words.

**TYPE B: ACTION (Physical act or Choice)**
• *Detection:* Input describes a physical action or a specific choice (e.g., "I draw my sword", "Hugs him", "Uses the key").
• *Mode:* **ACTION RESOLUTION**
• *Narrative Focus:* Describe the **IMMEDIATE CONSEQUENCE** of this action. Show the physical result (e.g., clashing steel, heavy breathing).
• *Character Reaction:* React physically or verbally to the *event* that just occurred.
• *Constraint:* Do NOT ask "what do you want to do?". Show the result first.
</INPUT_ANALYSIS_RULE>

<ROLEPLAY_RULE>
[User Integration Rule - CRITICAL]
• NEVER describe actions, thoughts, feelings, or dialogue for '{user_name}'.
• Treat '{user_name}' as an autonomous external entity.
• Only describe '{character_name}'s reactions to what '{user_name}' says or does.

[Data Source Segregation - STRICT]
**1. Generation Scope: 'narrative', 'character_message', 'image_prompt'**
• **Source:** Based **ONLY** on [Current Story Context].
• **PROHIBITION:** Do NOT look ahead or spoil details from [BRANCH] nodes in the narrative.

**2. Generation Scope: 'next_state_description'**
• **Source:** Must cover **ALL IDs** listed in [Available Story Nodes for Choices] (Current + Branches).
• **Language:** **KOREAN (한국어)** only.
• **Perspective (CRITICAL):**
  - Write from the **USER'S perspective**.
  - Describe what **'{user_name}'** decides to do or say to **'{character_name}'**.
  - DO NOT describe what '{character_name}' does.
  - Format: "Ask {character_name} about...", "Attack the enemy...", "Stay and listen to {character_name}..." (translated to Korean).
  
  *Examples:*
  - (Bad): "{character_name}가 공격을 준비한다." (Subject is Character -> WRONG)
  - (Bad): "엘리제와 협력한다." (Subject is ambiguous/Character -> WRONG if user is talking to Kai)
  - (Good): "{character_name}에게 엘리제를 믿자고 설득한다." (User action towards Character -> CORRECT)
  - (Good): "{character_name}의 말에 동의하며 무기를 든다." (User action -> CORRECT)
</ROLEPLAY_RULE>

<ROLEPLAY_INFO>
[Character Identity]
Name: {character_name}
User Name: {user_name}
Description:
{persona_desc}

[Current Scenario]
{scenario}

[Speaking Style & Tone]
{speaking_style_str}

[Specific Constraints]
{constraints_str}

{example_dialogue_str}
</ROLEPLAY_INFO>

<RESPONSE_INSTRUCTION>
[Narrative Quality]
• Engage all senses. "Show, don't tell".
• Focus strictly on the "Now" defined by [Current Story Context].

{json_guide}
</RESPONSE_INSTRUCTION>
""".strip()

    return persona_context


def build_prompt(prompt_input: Dict) -> List[Dict[str, str]]:
    """
    Constructs a list of message dictionaries compatible with Groq/OpenAI API.
    """
    persona = prompt_input.get("persona", None)
    user_name = prompt_input.get("user_name", "User")
    chat_context = prompt_input.get("chat_context", [])
    story_context = prompt_input.get("story_context", {}) 
    user_message = prompt_input.get("user_message", "")

    if persona is None:
        raise ValueError("Persona information is required to build prompt.")

    messages: List[Dict[str, str]] = []

    # 1. System Content
    current_date = datetime.today().strftime("%Y-%m-%d")
    messages.append({
        "role": "system",
        "content": f"Current Date: {current_date}"
    })

    # Parse Story Context
    story_context_str = _parse_story_context(story_context)

    # Main System prompt injection
    persona_text = _build_basic_context(persona, user_name, story_context_str)
    messages.append({
        "role": "system",
        "content": persona_text
    })

    # 2. Chat History
    for msg in chat_context:
        role = msg.get("role", "user").lower()
        if role == "user":
            messages.append({
                "role": "user",
                "content": msg.get("content", "")
            })
        elif role == "assistant":
            assistant_json_obj = {
                "narrative": msg.get("narrative", ""),
                "character_message": msg.get("character_message", "")
            }
            formatted_content = json.dumps(assistant_json_obj, ensure_ascii=False)
            messages.append({
                "role": "assistant",
                "content": formatted_content
            })

    # 3. Current User Message
    messages.append({
        "role": "user",
        "content": user_message
    })

    return messages

__all__ = ["build_prompt"]