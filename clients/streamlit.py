import streamlit as st
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

FASTAPI_URL = os.getenv("FASTAPI_URL", "")


st.set_page_config(
    page_title="Fitness Assistant",
    page_icon="💪",
    layout="centered"
)

st.title("💪 Fitness Assistant")
st.caption("Ask me anything about exercises, workouts, and fitness!. NB: This is just a simulator of a RAG application, you should be supervised a professional trainer before you engage in these workout")
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("image_urls"):
            cols = st.columns(len(msg["image_urls"]))
            for col, url in zip(cols, msg["image_urls"]):
                if url:
                    col.image(url, use_column_width=True)


query = st.chat_input("Ask about an exercise...")

if query:

    with st.chat_message("user"):
        st.write(query)
    
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.chat_message("assistant"):
        with st.spinner("Finding excercises..."):
            try:
                response = httpx.post(
                    f"{FASTAPI_URL}/api/v1/chat",
                    json={"query": query, "source": "streamlit"},
                    timeout=120
                )
                            
                if response.status_code == 429:
                    st.warning("⚠️ Too many requests. Please wait a minute before trying again.")
                
                elif response.status_code == 200:
                    
                    data = response.json()
                    answer = data.get("answer",{})
                    message = answer.get("message","")
                    image_urls = answer.get("image_urls",[])

                    st.write(message)
                    if image_urls:
                        st.markdown("#### Exercise Images")
                        cols = st.columns(len(image_urls))
                        for col, url in zip(cols, image_urls):
                            if url:
                                col.image(url, use_column_width =True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": message,
                        "image_urls": image_urls
                    })

                    def send_feedback(feedback_type):
                        response = httpx.post(
                            f"{FASTAPI_URL}/api/v1/feedback",
                            json={
                                "feedback": feedback_type,
                                "source": "streamlit",
                            }
                        )
                        print(f"Feedback status: {response.status_code}")
                    ## Feedback
                    st.markdown("#### Was this response useful")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.button("👍 Relevant", on_click=send_feedback,args=("relevant",))


                    with col2:
                        st.button("👎 Not Relevant", on_click=send_feedback,args=("non_relevant",))
                    
                else:
                    st.error("Something went wrong. Please try again.")

  
            except Exception as e:
                st.error(f"Could not connect to the server: {e}")
