import streamlit as st
from PIL import Image
from personas import PREDEFINED_PERSONAS, PERSONA_CATEGORIES
from feedback import get_openai_response,generate_user_story
from feedback import image_to_base64
from typing import Dict
import re, ast, json
from typing import Optional, Dict
from datetime import datetime

def _extract_json_object(text: str) -> Optional[str]:
    """Pull the first balanced {...} from a string, stripping ```json fences if present."""
    if not isinstance(text, str):
        return None
    t = text.strip()
    # strip code fences
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    # find first balanced JSON object
    start = t.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(t[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return t[start:i+1]
    return None

def parse_json_feedback(feedback_text: str) -> Dict:
    """Tolerant JSON parser for the model's output; returns a dict with safe defaults."""
    # Already a dict?
    if isinstance(feedback_text, dict):
        return feedback_text

    if not isinstance(feedback_text, str):
        feedback_text = str(feedback_text)

    # normalize quotes
    cand = (_extract_json_object(feedback_text) or feedback_text).strip()
    cand = cand.replace("“", '"').replace("”", '"').replace("’", "'")

    # 1) strict JSON
    try:
        data = json.loads(cand)
    except Exception:
        # 2) allow single quotes via ast
        try:
            data = ast.literal_eval(cand)
        except Exception:
            # 3) remove trailing commas before ] or }
            cand2 = re.sub(r",\s*([}\]])", r"\1", cand)
            try:
                data = json.loads(cand2)
            except Exception:
                data = None

    # fallbacks
    if not isinstance(data, dict):
        return {
            "Descriptive feedback": feedback_text,
            "What's you like": [],
            "What's you concern": [],
            "Safety": 3.0,
            "Comfort": 3.0,
            "Accessibility": 3.0,
            "Aesthetics": 3.0,
            "Social Interaction": 3.0,
        }

    # Ensure lists for likes/concerns
    data["What's you like"] = _normalize_points(data.get("What's you like"))
    data["What's you concern"] = _normalize_points(data.get("What's you concern"))
    return data

def _normalize_points(v):
    """Normalize bullet points from list or string."""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s or s.lower() == "none":
        return []
    # Try to parse JSON-ish array first
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
        try:
            arr = ast.literal_eval(s)
            if isinstance(arr, (list, tuple)):
                return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
    # Split on common separators
    if "•" in s:
        return [p.strip(" -•") for p in s.split("•") if p.strip(" -•")]
    if "; " in s:
        return [p.strip(" -•") for p in s.split(";") if p.strip(" -•")]
    if ", " in s and len(s.split(", ")) <= 6:
        return [p.strip(" -•") for p in s.split(",") if p.strip(" -•")]
    # Lines
    if "\n" in s:
        return [p.strip(" -•") for p in s.splitlines() if p.strip(" -•")]
    return [s]

def display_empathy_feedback(feedback, persona_name: str = "Persona"):
    """
    Render the model's initial JSON feedback in a friendly format:
      - Descriptive feedback box
      - Two columns for Likes & Concerns (bullets)
      - Score bars for 5 dimensions
    """
    data = parse_json_feedback(feedback)

    # Descriptive feedback
    st.markdown("### What I See, Think & Feel")
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; 
                border-left: 5px solid #667eea; margin: 10px 0;">
        <p style="font-size: 16px; line-height: 1.6; margin: 0; font-style: italic;">
            "{data.get('Descriptive feedback', 'No descriptive feedback provided.')}"
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Likes and Concerns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### What I Like")
        for like in data.get("What's you like", []):
            st.markdown(f"""
            <div style="background-color: #d4edda; padding: 10px; margin: 6px 0; 
                        border-radius: 8px; border-left: 4px solid #28a745;">
                <span style="color: #155724;">✓ {like}</span>
            </div>
            """, unsafe_allow_html=True)
        if not data.get("What's you like"):
            st.info("No specific likes mentioned")
    with col2:
        st.markdown("### What Concerns Me")
        for c in data.get("What's you concern", []):
            st.markdown(f"""
            <div style="background-color: #f8d7da; padding: 10px; margin: 6px 0; 
                        border-radius: 8px; border-left: 4px solid #dc3545;">
                <span style="color: #721c24;">⚠ {c}</span>
            </div>
            """, unsafe_allow_html=True)
        if not data.get("What's you concern"):
            st.success("No major concerns identified")

    # Scores
    st.markdown("### Detailed Evaluation Scores")
    categories = ["Safety", "Comfort", "Accessibility", "Aesthetics", "Social Interaction"]
    colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57"]
    for i, category in enumerate(categories):
        try:
            score = float(data.get(category, 3.0))
        except Exception:
            score = 3.0
        percentage = (max(0.0, min(5.0, score)) / 5.0) * 100
        st.markdown(f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: bold; font-size: 16px;">{category}</span>
                <span style="background-color: {colors[i]}; color: white; padding: 4px 8px; 
                           border-radius: 15px; font-weight: bold;">{score:.1f}/5</span>
            </div>
            <div style="background-color: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background-color: {colors[i]}; height: 100%; width: {percentage:.0f}%; 
                           border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)



def save_persona_to_history(persona, project_description, chat_history):
    """
    Snapshot the current conversation into session state so it shows up
    in the sidebar history (or wherever you list it later).
    """
    try:
        # Ensure containers exist
        if "persona_history" not in st.session_state:
            st.session_state.persona_history = []
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = {}

        # Build an ID and snapshot
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        pid = f"{persona.get('name','Persona')}-{ts}"

        entry = {
            "id": pid,
            "persona": persona,
            "project_description": project_description or "",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "messages": list(chat_history) if isinstance(chat_history, list) else [],
        }

        # Lightweight list for quick display
        st.session_state.persona_history.append({
            "id": entry["id"],
            "persona": entry["persona"],
            "project_description": entry["project_description"],
            "started_at": entry["started_at"],
        })

        # Full conversation lookup
        st.session_state.conversation_history[pid] = entry

        # (Optional) user feedback
        st.toast("Conversation saved to history.", icon="💾")
    except Exception as e:
        st.warning(f"Could not save conversation history: {e}")


def page_upload():
    """Page 1: Project upload and description"""
    st.title("Urban Design")
    # st.markdown("### Share your urban design project and get feedback from diverse community perspectives")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Project Description")
        project_description = st.text_area(
            "Describe your urban design project, its objectives, and key features:",
            value=st.session_state.project_description,
            height=200,
            placeholder="e.g., This is a mixed-use development proposal for downtown area, aiming to create affordable housing while preserving green spaces..."
        )
        st.session_state.project_description = project_description
    with col2:
        st.subheader("Upload Design Image")
        uploaded_file = st.file_uploader("Choose an image file (PNG, JPG, JPEG)", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file
            image = Image.open(uploaded_file)
            st.image(image, caption='Your uploaded design', use_container_width=True)
        elif st.session_state.uploaded_image is not None:
            image = Image.open(st.session_state.uploaded_image)
            st.image(image, caption='Your uploaded design', use_container_width=True)
    st.markdown("---")
    if st.button("Meet Your Role", type="primary", use_container_width=True):
        if project_description.strip():
            st.session_state.page = 'persona_choice'
            st.rerun()
        else:
            st.error("Please provide a project description before proceeding.")



def page_persona_choice():
    """Page 2: Choose between predefined or custom persona"""
    st.title(" Choose Your Role Member")
    st.markdown("### Who would you like to get feedback from?")
    if st.button("← Back to Project Upload"):
        st.session_state.page = 'upload'
        st.rerun()
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pre-defined Role")
        st.markdown("Choose from our diverse roles, each with unique backgrounds and perspectives.")
        if st.button("Select Pre-defined Role", type="primary", use_container_width=True):
            st.session_state.page = 'predefined_personas'
            st.rerun()
    with col2:
        st.subheader("Create New Role")
        st.markdown("Build a custom  roles based on specific demographics and characteristics you want to explore.")
        if st.button("Create Custom Role", type="primary", use_container_width=True):
            st.session_state.page = 'custom_persona'
            st.rerun()



def page_predefined_personas():
    """Page 3a: Select from predefined personas"""
    st.title("Role Member Profiles")
    if st.button("← Back to Role Choice"):
        st.session_state.page = 'persona_choice'
        st.rerun()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Select a Role Member:")
        for persona_key, persona_info in PREDEFINED_PERSONAS.items():
            if st.button(f"{persona_info['name']} - {persona_key}", key=persona_key, use_container_width=True):
                st.session_state.temp_selected_persona = persona_info
                st.rerun()
    with col2:
        st.subheader("Role Details")
        if st.session_state.get('temp_selected_persona'):
            persona = st.session_state.temp_selected_persona
            st.markdown(f"**Name:** {persona['name']}")
            st.markdown(f"**Age:** {persona['age']}")
            st.markdown(f"**Gender:** {persona['gender']}")
            st.markdown(f"**Frequency of use:** {persona['frequency_of_use']}")
            st.markdown("**Reason for visiting:**")
            for reason in persona['reason_for_visiting']:
                st.markdown(f"• {reason}")
            st.markdown("**Mobility habits:**")
            for habit in persona['mobility_habits']:
                st.markdown(f"• {habit}")
            st.markdown("**Accessibility needs:**")
            for need in persona['accessibility_needs']:
                st.markdown(f"• {need}")
            st.markdown("**Other values:**")
            for value in persona['other_values']:
                st.markdown(f"• {value}")
            st.markdown("**User Story:**")
            st.markdown(persona['user_story'])
            st.markdown("---")
            if st.button("Choose this Role", type="primary", use_container_width=True):
                st.session_state.selected_persona = persona
                st.session_state.page = 'feedback'
                st.rerun()
        else:
            st.info("Click on a role member to see their detailed information")



def page_custom_persona():
    """Page 3b: Create custom persona"""
    st.title("Create Your Custom Role")
    if st.button("← Back to Role Choice"):
        st.session_state.page = 'persona_choice'
        st.rerun()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Role Details")
        persona_data = {}
        for category, description in PERSONA_CATEGORIES.items():
            if category == "Place":
                persona_data[category.lower()] = st.text_input(
                    f"{category}", placeholder="e.g., Downtown Park, Main Street, Community Center", help=description
                )
            elif category == "Age":
                persona_data[category.lower()] = st.number_input(f"{category}", min_value=18, max_value=100, value=35, help=description)
            elif category == "Gender":
                persona_data[category.lower()] = st.selectbox(f"{category}", ["Woman", "Man", "Non-binary", "Prefer not to say", "Other"], help=description)
            elif category == "Frequency of use":
                persona_data[category.lower().replace(' ', '_')] = st.selectbox(f"{category}", ["Daily", "Several times a week", "Weekly", "Monthly", "Occasionally", "Rarely"], help=description)
            elif category == "Reason for visiting":
                persona_data[category.lower().replace(' ', '_')] = st.text_area(f"{category}", placeholder="e.g., walking my dog, meeting friends, commuting to work, exercising", help=description)
            elif category == "Mobility habits":
                persona_data[category.lower().replace(' ', '_')] = st.multiselect(f"{category}", ["Walking", "Cycling", "Public transit", "Driving", "Wheelchair", "Mobility aid", "Other"], help=description)
            elif category == "Accessibility needs":
                persona_data[category.lower().replace(' ', '_')] = st.text_area(f"{category}", placeholder="e.g., wheelchair accessible paths, audio signals, good lighting, seating areas", help=description)
            elif category == "Other values":
                persona_data[category.lower().replace(' ', '_')] = st.text_area(f"{category}", placeholder="e.g., environmental sustainability, community connection, safety, inclusivity", help=description)
        if st.button("Generate Role Story", type="primary"):
            if persona_data.get('place') and persona_data.get('age'):
                if isinstance(persona_data.get('mobility_habits', ''), list):
                    persona_data['mobility'] = ', '.join(persona_data['mobility_habits'])
                else:
                    persona_data['mobility'] = persona_data.get('mobility_habits', '')
                with st.spinner("Generating Role story..."):
                    user_story = generate_user_story(persona_data)
                custom_persona = {
                    'name': f"{persona_data.get('age')}-year-old {persona_data.get('gender', 'Person')}",
                    'age': persona_data.get('age'),
                    'place': persona_data.get('place'),
                    'gender': persona_data.get('gender'),
                    'frequency': persona_data.get('frequency_of_use'),
                    'reasons': persona_data.get('reason_for_visiting'),
                    'mobility': persona_data.get('mobility', ''),
                    'accessibility': persona_data.get('accessibility_needs'),
                    'values': persona_data.get('other_values'),
                    'story': user_story,
                    'background': f"Regular user of {persona_data.get('place', 'the area')}, visits {persona_data.get('frequency_of_use', 'regularly')}",
                    'concerns': ['Community well-being', 'Accessibility', 'Safety'],
                    'tone': 'Personal and experience-based'
                }
                st.session_state.custom_persona = custom_persona
                st.session_state.selected_persona = custom_persona
            else:
                st.error("Please fill in at least the Place and Age fields.")
    with col2:
        st.subheader("Generated Role Story")
        if st.session_state.custom_persona:
            persona = st.session_state.custom_persona
            st.success("Role Generated!")
            st.markdown(f"**Place:** {persona.get('place', 'N/A')}")
            st.markdown(f"**Age:** {persona.get('age', 'N/A')}")
            st.markdown(f"**Gender:** {persona.get('gender', 'N/A')}")
            st.markdown(f"**Frequency of use:** {persona.get('frequency', 'N/A')}")
            st.markdown(f"**Mobility:** {persona.get('mobility', 'N/A')}")
            st.markdown("---")
            st.markdown("**Generated User Story:**")
            st.markdown(persona.get('story', 'No story generated'))
            st.markdown("---")
            if st.button("Get Feedback from This Role", type="primary", use_container_width=True):
                st.session_state.page = 'feedback'
                st.rerun()
        else:
            st.info("👈 Fill in the form and click 'Generate User Story' to create your custom role")

# ---------- JSON parsing + bullet normalization helpers ----------



def page_feedback():
    """Page 4: Chat with selected persona"""
    if not st.session_state.selected_persona:
        st.error("No persona selected. Please go back and select a persona.")
        return

    persona = st.session_state.selected_persona
    st.title(f"Feedback from {persona['name']}")
    if 'occupation' in persona:
        st.markdown(f"**{persona['occupation']}, Age {persona['age']}**")
    elif 'gender' in persona:
        st.markdown(f"**{persona['age']}-year-old {persona['gender']}**")
    else:
        st.markdown(f"**Age {persona['age']}**")

    if st.button("← Back to Role Selection"):
        st.session_state.page = 'predefined_personas' if st.session_state.custom_persona is None else 'custom_persona'
        st.session_state.chat_history = []
        st.rerun()

    if not st.session_state.chat_history:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.subheader("Your Design")
            if st.session_state.uploaded_image:
                image = Image.open(st.session_state.uploaded_image)
                st.image(image, caption='Your urban design', use_container_width=True)
            else:
                st.info("No image uploaded")
            st.markdown("### Project Description")
            st.markdown(f"""
            <div style="background-color: #f1f3f4; padding: 15px; border-radius: 10px; 
                        border-left: 4px solid #4285f4;">
                {st.session_state.project_description}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.subheader(f"💬 {persona['name']}'s Feedback")
            with st.spinner(f"Getting feedback from {persona['name']}..."):
                initial_feedback = get_openai_response(
                    persona, 
                    st.session_state.project_description,
                    st.session_state.uploaded_image
                )
                display_empathy_feedback(initial_feedback, persona['name'])
                st.session_state.chat_history.append({'role': 'persona','content': initial_feedback})
    else:
        st.markdown("---")
        st.subheader("Continue the Conversation")

        facts_for_ui = st.session_state.get("last_top_facts", [])

        with st.expander("Local facts used (top matches)", expanded=False):
            if facts_for_ui:
                for f in facts_for_ui:
                    st.markdown(f"- **{f.get('id','?')}** — {f.get('title','(no title)')}")
            else:
                st.caption("No retrieved facts for this turn yet.")

        with st.expander("Your Project Summary", expanded=False):
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.session_state.uploaded_image:
                    image = Image.open(st.session_state.uploaded_image)
                    st.image(image, caption='Your design', use_container_width=True)
            with col2:
                st.write(f"**Description:** {st.session_state.project_description}")
        for i, message in enumerate(st.session_state.chat_history):
            if i == 0 and message['role'] == 'persona':
                continue
            if message['role'] == 'persona':
                with st.chat_message("assistant", avatar="🙎‍♀️"):
                    st.write(f"**{persona['name']}:** {message['content']}")
            else:
                with st.chat_message("user", avatar="👨‍💼"):
                    st.write(f"**You:** {message['content']}")
    user_input = st.chat_input(f"Ask {persona['name']} a question about your project...")
    if user_input:
        st.session_state.chat_history.append({'role': 'user','content': user_input})
        with st.spinner(f"{persona['name']} is thinking..."):
            response = get_openai_response(
                persona, 
                st.session_state.project_description,
                st.session_state.uploaded_image,
                user_input
            )
            st.session_state.chat_history.append({'role': 'persona','content': response})
        st.rerun()

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Try Another Role"):
            if st.session_state.chat_history:
                save_persona_to_history(persona, st.session_state.project_description, st.session_state.chat_history)
            st.session_state.page = 'persona_choice'
            st.session_state.chat_history = []
            st.session_state.selected_persona = None
            st.rerun()
    with col2:
        if st.button("New Project"):
            if st.session_state.chat_history:
                save_persona_to_history(persona, st.session_state.project_description, st.session_state.chat_history)
            st.session_state.page = 'upload'
            st.session_state.chat_history = []
            st.session_state.selected_persona = None
            st.session_state.uploaded_image = None
            st.session_state.project_description = ""
            st.rerun()
    with col3:
        if st.button("Export Conversation"):
            if st.session_state.chat_history:
                save_persona_to_history(persona, st.session_state.project_description, st.session_state.chat_history)
            conversation_text = f"Urban Design Feedback Session\n"
            conversation_text += f"Project: {st.session_state.project_description}\n"
            if 'occupation' in persona:
                conversation_text += f"Community Member: {persona['name']} ({persona['occupation']})\n\n"
            elif 'gender' in persona:
                conversation_text += f"Community Member: {persona['name']} ({persona['age']}-year-old {persona['gender']})\n\n"
            else:
                conversation_text += f"Community Member: {persona['name']}\n\n"
            for message in st.session_state.chat_history:
                if message['role'] == 'persona':
                    conversation_text += f"{persona['name']}: {message['content']}\n\n"
                else:
                    conversation_text += f"You: {message['content']}\n\n"
            st.download_button(
                label="Download Conversation",
                data=conversation_text,
                file_name=f"feedback_{persona['name'].replace(' ', '_')}.txt",
                mime="text/plain"
            )

# Main app routing

