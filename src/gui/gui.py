import streamlit as st
from langserve import RemoteRunnable

"""WARNING THIS IS AI - ALWAYS VERIFY YOUR QUESTIONS"""
agent = RemoteRunnable("http://localhost:8000/agent")

st.title("Medical Fact-Checker Agentic System")
video_url = st.text_input("Input YouTube link:")

if st.button("Start Analyst"):
    status_box = st.empty() 
    results_container = st.container() 
    
    input_data = {"video_url": video_url}
    
    try:
        current_step = "Start"
        final_error = None
        for chunk in agent.stream(input_data, config={"metadata": {"conversation_id": "123"}}):
            
            
            for node_name, state_update in chunk.items():
                if node_name == "subgraph" and state_update is None:
                    continue
                if state_update is None:
                    st.error(f"Error: Received None for node {node_name}")
                    break
                if state_update.get("error"):
                    final_error = state_update["error"]
                    break
                if node_name == "ingest":
                    status_box.info(f"✅ Downloaded video data.")
                
                elif node_name == "gatekeeper":
                    verdict = state_update.get("gatekeeper_verdict")
                    if verdict == "end":
                        status_box.error("⛔ Gatekeeper refused (none medical data).")
                    else:
                        status_box.info("✅ Gatekeeper confirmed data.")
                        
                elif node_name == "extractor":
                    status_box.info(f"⛏️ Extractor processing claims...")
                
                elif node_name == "refiner":
                    claims_count = len(state_update.get("unique_claims", []))
                    status_box.info(f"🧠 Refiner: Found {claims_count} unique claims.")
                    
                elif node_name == "reporter":
                    final_report = state_update.get("final_report")
                    status_box.success("🎉 Raport ready!")
                    results_container.markdown(final_report)
        if final_error:
            st.error("Error in processing {final_error}")
        else:
            st.success("READY!")

    except Exception as e:
        st.error(f"Communication error: {e}")