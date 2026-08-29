import streamlit as st
from openai import OpenAI
import anthropic
import google.generativeai as genai

st.set_page_config(page_title="Peach Powered AI", page_icon="🍑", layout="wide")
st.title("Peach Powered AI 🍑")

# Drop your keys here
openai_key = "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"
anthropic_key = "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"
google_key = "AQ.Ab8RN6LKJ-yqTq27kE-K2XWmg1gbSHP1ZbdX54Q4fl9xeSg3-Q"

# Initialize session state for onboarding
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
    st.session_state.user_background = ""
    st.session_state.user_goals = ""

if not st.session_state.onboarded:
    st.subheader("Welcome to Peach Powered AI! Let's set up your profile.")
    with st.form("onboarding_form"):
        bg_input = st.text_area("1. What's your background, preferred tech stack, or general field?")
        goals_input = st.text_area("2. What active projects, builds, or main goals are you working on right now?")
        submitted = st.form_submit_button("Lock In Profile")
        
        if submitted:
            st.session_state.user_background = bg_input
            st.session_state.user_goals = goals_input
            st.session_state.onboarded = True
            st.rerun()
else:
    st.sidebar.title("Peach Controls 🍑")
    with st.sidebar.expander("Update Profile Info"):
        st.session_state.user_background = st.text_area("Background:", value=st.session_state.user_background)
        st.session_state.user_goals = st.text_area("Goals / Projects:", value=st.session_state.user_goals)

    st.sidebar.markdown("---")
    st.subheader("Feed Custom Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Drop notes, text files, or PDFs here:", 
        type=["txt", "md", "pdf"], 
        accept_multiple_files=True
    )
    
    document_context = ""
    if uploaded_files:
        for file in uploaded_files:
            try:
                content = file.read().decode("utf-8")
                document_context += f"\n--- Document: {file.name} ---\n{content}\n"
            except Exception:
                pass

    st.write("Type your prompt below, or use the microphone to speak your query directly from your device.")

    # Input method selection: Text or Voice
    input_mode = st.radio("Choose Input Mode:", ["Text", "Voice Recorder"], horizontal=True)
    
    user_prompt = ""

    if input_mode == "Text":
        user_prompt = st.chat_input("Ask the council...")
    else:
        audio_file = st.audio_input("Record your prompt to the council:")
        if audio_file is not None:
            with st.spinner("Transcribing your voice..."):
                try:
                    client_openai = OpenAI(api_key=openai_key)
                    # Use OpenAI Whisper to convert speech audio to text
                    transcript = client_openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=("audio.wav", audio_file.read(), "audio/wav")
                    )
                    user_prompt = transcript.text
                    st.success(f"Transcribed: \"{user_prompt}\"")
                except Exception as e:
                    st.error(f"Transcription Error: {e}")

    if user_prompt:
        st.chat_message("user").write(user_prompt)
        
        gpt_ans, claude_ans, gemini_ans = "", "", ""
        
        with st.spinner("Consulting ChatGPT, Claude, and Gemini..."):
            try:
                client_openai = OpenAI(api_key=openai_key)
                r_gpt = client_openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": user_prompt}]
                )
                gpt_ans = r_gpt.choices[0].message.content
            except Exception as e:
                gpt_ans = f"[OpenAI Error: {e}]"

            try:
                client_anthropic = anthropic.Anthropic(api_key=anthropic_key)
                r_claude = client_anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                claude_ans = r_claude.content[0].text
            except Exception as e:
                claude_ans = f"[Claude Error: {e}]"

            try:
                genai.configure(api_key=google_key)
                model_gemini = genai.GenerativeModel("gemini-1.5-pro")
                r_gemini = model_gemini.generate_content(user_prompt)
                gemini_ans = r_gemini.text
            except Exception as e:
                gemini_ans = f"[Gemini Error: {e}]"


        with st.spinner("Synthesizing the ultimate answer..."):
            synth_prompt = f"""
            You are an expert synthesizer for the user. 
            
            USER BACKGROUND:
            {st.session_state.user_background}
            
            USER GOALS & PROJECTS:
            {st.session_state.user_goals}
            
            UPLOADED DOCUMENTS / REFERENCE DATA:
            {document_context if document_context else "None provided."}
            
            The user asked: "{user_prompt}"
            
            Here are three separate responses generated by different AI models:
            --- CHATGPT ---
            {gpt_ans}
            
            --- CLAUDE ---
            {claude_ans}
            
            --- GEMINI ---
            {gemini_ans}
            
            Please synthesize these perspectives into a single, cohesive, highly customized final answer tailored specifically to the user's background, active projects, and uploaded references.
            """
            
            try:
                client_openai = OpenAI(api_key=openai_key)
                r_synth = client_openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": synth_prompt}]
                )
                final_answer = r_synth.choices[0].message.content
                st.chat_message("assistant").write(final_answer)
                
            except Exception as e:
                st.error(f"Synthesis Error: {e}")
