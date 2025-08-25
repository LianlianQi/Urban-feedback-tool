from typing import Dict
from PIL import Image
import streamlit as st

from client import get_openai_client, CURRENT_MODEL
from prompts import VOICE_GUIDE
from rag import load_facts, _facts_checksum, embed_facts, retrieve_facts

def image_to_base64(image):
    """Convert PIL Image to base64 string for OpenAI API"""
    import base64
    import io

    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode('utf-8')



def get_openai_response(persona_info: Dict, project_description: str, uploaded_image=None, user_message: str = "") -> str:
    """Generate AI response using gpt-4o-mini with multimodal capabilities, handling both generated and custom personas."""
    try:
        # --- Load facts and build (or reuse) the index WITHOUT passing a client to cached funcs ---
        facts = load_facts()
        checksum = _facts_checksum(facts)

        if ('facts_embs' not in st.session_state) or (st.session_state.get('facts_checksum') != checksum):
            with st.spinner("Indexing local facts..."):
                st.session_state.facts_embs = embed_facts(facts, _checksum=checksum)
                st.session_state.facts_checksum = checksum

        # Pull relevant facts for this request (use user_message for follow-ups)
        top_facts = retrieve_facts(
            facts, st.session_state.facts_embs,
            persona_info, project_description, user_message or "", k=5
        )
        # Save for UI use outside this function
        st.session_state["last_top_facts"] = top_facts

        def _compact_fact(f):
            when = f.get("time", {}).get("as_of", "")
            return f"[{f['id']}] {f['title']} — {f['summary']} (as of {when})"

        facts_block = "\n".join(_compact_fact(f) for f in top_facts)

        # --- OpenAI client (not passed into cached funcs) ---
        client = get_openai_client()
        if not client:
            return "❌ Could not connect to OpenAI. Please check your API key."

        CURRENT_MODEL = "gpt-4o-mini"

        # --- Normalize persona fields (handles both lowercase keys and custom persona form keys) ---
        place = persona_info.get('place') or persona_info.get('Place') or "the local area"
        age = persona_info.get('age') or persona_info.get('Age', 'adult')
        gender = persona_info.get('gender') or persona_info.get('Gender', 'resident')
        frequency = persona_info.get('frequency') or persona_info.get('Frequency of use') or persona_info.get('frequency_of_use', 'regular')
        reasons = persona_info.get('reasons') or persona_info.get('Reason for visiting') or persona_info.get('reason_for_visiting', 'various reasons')
        values = persona_info.get('values') or persona_info.get('Personal values') or persona_info.get('personal_values', 'community well-being')
        mobility = persona_info.get('mobility') or persona_info.get('Mobility habits') or persona_info.get('mobility_habits', 'standard mobility')
        accessibility = persona_info.get('accessibility') or persona_info.get('Accessibility needs') or persona_info.get('accessibility_needs', 'none specified')
        story = persona_info.get('story') or persona_info.get('user_story') or ""

        # Ensure lists are joined
        if isinstance(reasons, list): reasons = ", ".join(reasons)
        if isinstance(values, list): values = ", ".join(values)
        if isinstance(mobility, list): mobility = ", ".join(mobility)
        if isinstance(accessibility, list): accessibility = ", ".join(accessibility)

        # Persona profile text
        persona_text = f"""
- Age: {age}
- Gender: {gender}
- Lives in: {place}
- Frequency of use: {frequency}
- Reason for visiting: {reasons}
- Values: {values}
- Mobility habits: {mobility}
- Accessibility needs: {accessibility}
- Background: {story}
"""

        # ----------------------
        # FOLLOW-UP CHAT BRANCH
        # ----------------------
        if user_message:
            system_prompt = f"""
You are a long-term resident with the following characteristics:
{persona_text}

You are continuing to provide feedback on an urban design project in {place}.
You have access to both the project description and the project image.
Carefully examine the image to identify and mention relevant urban furniture, seating, vegetation, paths, lighting, and other design elements.

You also have access to local, structured facts (IDs + summaries):
{facts_block}
Prefer these facts when relevant; do not invent new facts.
If a fact seems unrelated, ignore it.

Respond in your persona's voice, referencing what you see in the image when relevant.
{VOICE_GUIDE}
"""

            messages = [{"role": "system", "content": system_prompt}]

            # Add project description + image
            if uploaded_image:
                image = Image.open(uploaded_image)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Project description: {project_description}"},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{image_to_base64(image)}",
                            "detail": "high"
                        }}
                    ]
                })
            else:
                messages.append({"role": "user", "content": f"Project description: {project_description}"})

            # Add follow-up question
            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=CURRENT_MODEL,
                messages=messages,
                temperature=0.4,
                max_tokens=500
            )
            return response.choices[0].message.content

        # ----------------------
        # INITIAL FEEDBACK BRANCH
        # ----------------------
        else:
            system_prompt = f"""
You are a long-term resident of {place}, and you have lived there for several years.
You have the following characteristics:
{persona_text}

Your role is to assist urban designers in evaluating their proposed design for {place}.
You will be provided with:
- A designed image created by an urban designer.
- A brief text description explaining the design intent and changes.

Based on your persona, the project description, and the project image, provide honest, empathetic, and experience-based feedback.
Carefully examine the image to identify and mention relevant urban furniture, seating, vegetation, paths, lighting, and other design details.
Please return your feedback strictly in the following JSON format:
{{
  "Descriptive feedback": "",
  "What's you like": "",
  "What's you concern": "",
  "Safety": 0.0,
  "Comfort": 0.0,
  "Accessibility": 0.0,
  "Aesthetics": 0.0,
  "Social Interaction": 0.0 
}}

Guidance:
- "Descriptive feedback" should reflect your own lived perspective using empathy map style: what you see, hear, think, and feel when experiencing the design.
- "What's you like" and "What's you concern" should be concise, max 3 bullet points each. If none, write "None".
- Scores: numeric between 0.0 and 5.0 based on your subjective evaluation.
- Do not generate content outside the specified JSON format.

Use the following local facts when relevant (IDs shown for context):
{facts_block}
"""

            if uploaded_image:
                image = Image.open(uploaded_image)
                response = client.chat.completions.create(
                    model=CURRENT_MODEL,
                    response_format={"type": "json_object"}, 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Project description: {project_description}"},
                                {"type": "image_url", "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_to_base64(image)}",
                                    "detail": "high"
                                }}
                            ]
                        }
                    ],
                    temperature=0.4,
                    max_tokens=1000
                )
            else:
                response = client.chat.completions.create(
                    model=CURRENT_MODEL,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Project description: {project_description}"}
                    ],
                    temperature=0.4,
                    max_tokens=1000
                )

            return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error connecting to OpenAI: {str(e)}\n\nPlease check:\n1. Your API key is correct\n2. You have sufficient OpenAI credits\n3. Your internet connection is stable"





def generate_user_story(persona_data: Dict) -> str:
    """
    Generate a short first-person user story for a custom persona.
    Robust against key naming differences (Place/place, Frequency of use/frequency_of_use, etc.)
    and avoids .format() brace collisions by injecting a prebuilt JSON blob.
    """
    import json

    try:
        client = get_openai_client()
        if not client:
            return "❌ Could not connect to OpenAI. Please check your API key."

        # --- Normalize incoming fields to handle both your form keys and internal keys ---
        place = (persona_data.get('place')
                 or persona_data.get('Place')
                 or "")
        age = (persona_data.get('age')
               or persona_data.get('Age')
               or "")
        gender = (persona_data.get('gender')
                  or persona_data.get('Gender')
                  or "")
        frequency = (persona_data.get('frequency')
                     or persona_data.get('frequency_of_use')
                     or persona_data.get('Frequency of use')
                     or "")
        reasons = (persona_data.get('reasons')
                   or persona_data.get('reason_for_visiting')
                   or persona_data.get('Reason for visiting')
                   or "")
        mobility = (persona_data.get('mobility')
                    or persona_data.get('mobility_habits')
                    or persona_data.get('Mobility habits')
                    or "")
        accessibility = (persona_data.get('accessibility')
                         or persona_data.get('accessibility_needs')
                         or persona_data.get('Accessibility needs')
                         or "")
        values = (persona_data.get('values')
                  or persona_data.get('personal_values')
                  or persona_data.get('Personal values')
                  or "")

        # Lists → readable strings
        def _to_str(v):
            if isinstance(v, list):
                return ", ".join(str(x) for x in v if str(x).strip())
            return str(v)

        persona_json_obj = {
            "Place": _to_str(place),
            "Age": _to_str(age),
            "Gender": _to_str(gender),
            "Frequency of use": _to_str(frequency),
            "Reason for visiting": _to_str(reasons),
            "Mobility habits": _to_str(mobility),
            "Accessibility needs": _to_str(accessibility),
            "Personal values": _to_str(values),
        }

        # Build prompt safely: inject a single JSON blob
        persona_json_str = json.dumps(persona_json_obj, ensure_ascii=False, indent=2)

        prompt = (
            "You are a user story generator for urban design research.\n"
            "You will be provided with a custom persona profile filled in by a user.\n"
            "Your goal is to generate a vivid, empathetic, first-person narrative that reflects this person's relationship with their local urban environment (e.g., park, street, square, playground).\n"
            "Use a natural human tone. Include contextual details (e.g., time of day, companions, what they see/do/feel/remember). "
            "Keep it grounded and believable, focused on needs and values related to the space.\n"
            "---\n"
            "Persona Profile Input:\n"
            f"{persona_json_str}\n"
            "---\n"
            "Write a first-person user story starting naturally, for example:\n"
            "\"I am a {Age} years old {Gender}. I've lived in {Place} for several years...\" or "
            "\"Every {Frequency of use}, I come here because...\"\n"
            "User story must be ≤150 words.\n"
            "Output:\n"
            "<USER STORY>"
        )

        # Use a vision-capable, instruction-following model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful writing assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=200
        )
        return response.choices[0].message.content

    except Exception as e:
        # Fallback demo story so your UI never blocks
        age = persona_data.get('age') or persona_data.get('Age') or '30'
        gender = persona_data.get('gender') or persona_data.get('Gender') or 'person'
        place = persona_data.get('place') or persona_data.get('Place') or 'this neighborhood'
        return (
            f"❌ API Error: {str(e)}\n\n"
            f"**Demo Story:** I am a {age}-year-old {gender} who has been part of {place} for several years. "
            "I find myself drawn to this space because it represents more than just a physical location—it's where my daily life unfolds."
        )

