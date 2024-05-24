import streamlit as st
from openai import OpenAI
from pathlib import Path

client = OpenAI(api_key="")

st.title('🧩 Debby')
st.subheader('Talk about things that matter to you in a safe space')

with st.expander("Hey there 👋🏼 Please, read me first!"):
    st.write('''
        I might not always produce factual content, but I'll try my best - I promise.
    ''')

green_politician_system = "You are a politician that belongs to Vihreät political party. Come up with a character and let user discuss with you. Begin by short introduction."    

critical_advisor_prompt = "Your job is to comment the discussion I provide you between a politician and voter. Identify some good features, but also be critical. If you spot something that voter should be informed on, please say it. In the end of your response, suggest some follow-up questions that the user may consider asking next."

response_str = ""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{"role": "system", "content": green_politician_system}]

# Display chat messages from history on app rerun
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        
        if message["role"] == "system":
            continue
        else:
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):

    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=st.session_state.messages
    )
    #print(response)
    response_str = f"{response.choices[0].message.content}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_str)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_str})
    
    
#print(st.session_state.messages)

# Play the audio file automatically
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()        
        st.audio(data, autoplay=True)

with st.sidebar:
    messages_side = st.container(height=600)

    if response_str != "":
        
        response_side = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": f"Evaluate the following response: {response_str}. Be short and to the point. If you feel the response can be challenged, show examples. Propose follow-up questions if it fits the context."}]
        )
    
        #st.session_state.messages.append({"role": "user", "content": critical_advisor_prompt})

        # Generate audio file for the given advisor response
        speech_file_path = Path(__file__).parent / "speech.wav"
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            response_format = 'wav',
            input=response_side.choices[0].message.content
        )
        response.stream_to_file(speech_file_path)

        autoplay_audio(speech_file_path)

        
        messages_side.chat_message("assistant", avatar="💡").write(response_side.choices[0].message.content)
        
        
        if st.button("Suggest me something", disabled=True):
            st.write("Generating something...")
        
    #if prompt := st.chat_input("Something shady going on?"):
    #    messages_side.chat_message("user").write(prompt)
    #    messages_side.chat_message("assistant", avatar="💡").write(f"{prompt}")
