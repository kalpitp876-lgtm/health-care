import streamlit as st
from agent import make_agent, ask_agent, MODEL_NAME
from knowledge_base import reindex_documents

st.set_page_config(page_title="Patient Triage & Reference Assistant", page_icon="🩺", layout="centered")
st.title("🩺 Patient Triage & Reference Assistant")
st.caption("Educational prototype • local Ollama model • public reference documents")

st.warning(
    "Medical safety notice: This educational tool is not a substitute for professional medical advice, "
    "diagnosis, or treatment. It may miss emergencies and its sample triage rules are not clinically validated. "
    "If you may be experiencing an emergency, contact your local emergency number now."
)

with st.sidebar:
    st.subheader("Setup status")
    st.write(f"Configured Ollama model: `{MODEL_NAME}`")
    st.write("Reference folder: `docs/`")
    st.write("Add official public PDF/TXT medical references to `docs/`, then rebuild the index.")
    if st.button("Rebuild reference index"):
        with st.spinner("Rebuilding local index..."):
            try:
                st.success(reindex_documents())
            except Exception as exc:
                st.error(f"Indexing failed: {exc}")
    st.caption("Do not upload patient records or personally identifying health information.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = None

for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

prompt = st.chat_input("Ask about a symptom or medication...")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Checking local references and applying the available rules..."):
            try:
                if st.session_state.agent is None:
                    st.session_state.agent = make_agent()
                answer = ask_agent(st.session_state.agent, prompt)
            except Exception as exc:
                answer = (
                    "The assistant could not run. Check that Ollama is running, the model is downloaded, "
                    "and dependencies are installed.\n\n"
                    f"Technical detail: `{type(exc).__name__}: {exc}`"
                )
            st.markdown(answer)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

st.caption("Prototype only. Triage rules are intentionally limited and must not be used to rule out emergencies.")
