import streamlit as st
import requests

# -------------- CONFIG ----------------
BACKEND_URL = "http://127.0.0.1:5000/query"

st.set_page_config(page_title="Real Estate Chatbot", layout="wide")
st.title("🏡 Real Estate AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------- DISPLAY CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -------------- USER INPUT ----------------
user_input = st.chat_input("Ask something like: 3BHK in Pune under 1 Cr")

if user_input:

    # Show user message
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send request to backend
    with st.chat_message("assistant"):
        with st.spinner("Searching Properties..."):
            try:
                response = requests.post(BACKEND_URL, json={"query": user_input})

                if response.status_code != 200:
                    st.error("⚠️ Server error. Check backend.")
                    st.stop()

                data = response.json()

                summary = data["summary"]
                results = data["results"]

                # Show summary
                st.write(summary)

                # st.write("### 🔍 Matched Properties")
                # st.write("---")

                # # Display each property card
                # for item in results:
                #     st.markdown(f"""
                #     #### ✅ {item['projectName']}

                #     **City:** {item['city']}  
                #     **BHK:** {item['type']}  
                #     **Price:** ₹{item['price']:,}  
                #     **Status:** {item['status']}  
                #     **Landmark:** {item['landmark']}  
                #     **Address:** {item['fullAddress']}  

                #     ---
                #     """)

                # Add assistant message to history
                st.session_state.messages.append(
                    {"role": "assistant", "content": summary}
                )

            except Exception as e:
                st.error("❌ Couldn't connect to Flask backend")
                st.exception(e)
