import streamlit as st
from ui_pages import (
    page_upload, page_persona_choice, page_predefined_personas,
    page_custom_persona, page_feedback
)

st.set_page_config(page_title="Urban Design Community Feedback", page_icon="🏙️", layout="wide")

# Session defaults
defaults = {
    'page': 'upload',
    'uploaded_image': None,
    'project_description': "",
    'selected_persona': None,
    'custom_persona': None,
    'chat_history': [],
    'persona_history': [],
    'conversation_history': {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def sidebar_nav():
    with st.sidebar:
        if st.button("Upload / Start Over", use_container_width=True):
            st.session_state.page = 'upload'; st.rerun()
        st.button("Persona Choice", on_click=lambda: st.session_state.update(page='persona_choice'), use_container_width=True)
        st.button("Predefined Personas", on_click=lambda: st.session_state.update(page='predefined_personas'), use_container_width=True)
        st.button("Custom Persona", on_click=lambda: st.session_state.update(page='custom_persona'), use_container_width=True)
        st.button("Feedback", on_click=lambda: st.session_state.update(page='feedback'), use_container_width=True)

def main():
    sidebar_nav()
    page = st.session_state.get('page', 'upload')
    if page == 'upload':
        page_upload()
    elif page == 'persona_choice':
        page_persona_choice()
    elif page == 'predefined_personas':
        page_predefined_personas()
    elif page == 'custom_persona':
        page_custom_persona()
    elif page == 'feedback':
        page_feedback()
    else:
        st.error(f"Unknown page: {page}")

if __name__ == "__main__":
    main()
