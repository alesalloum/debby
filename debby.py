import streamlit as st
from openai import OpenAI
from pathlib import Path
import time


client = OpenAI(api_key="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")

# Init prompts
green_politician_system = "You are a politician that belongs to Vihreät political party. Come up with a character and let user discuss with you. Begin by short introduction."    
finns_politician_system = "You are a politician that belongs to Perussuomalaiset political party. Come up with a character and let user discuss with you. Begin by short introduction."
critical_advisor_prompt = "Your job is to comment the discussion I provide you between a politician and voter. Identify some good features, but also be critical. If you spot something that voter should be informed on, please say it. In the end of your response, suggest some follow-up questions that the user may consider asking next."
response_str = ""

st.title('🧩 Debby')
st.subheader('Talk about things that matter to you in a safe space')

with st.expander("Hey there 👋🏼 Please, read me first!"):
    st.write('''
        I might not always produce factual content, but I'll try my best - I promise.
    ''')

# Initialize the session state for party_toggle if not already set
if 'party_toggle' not in st.session_state:
    st.session_state.party_toggle = 'Green Party'

# Initialize the session state for side bar
if 'sidebar_enabled' not in st.session_state:
    st.session_state.sidebar_enabled = True

# Initialize messages based on selected politician
def init_messages():
    st.session_state.messages = []
    chosen_politician = green_politician_system if st.session_state.party_toggle == 'Green Party' else finns_politician_system
    st.session_state.messages = [{"role": "system", "content": chosen_politician}]

# Callback function for siderbar toggle
def toggle_sidebar():
    if st.session_state.sidebar_enabled:
        st.session_state.sidebar_enabled = False
    else:
        st.session_state.sidebar_enabled = True


# Initialize chat history
if 'messages' not in st.session_state:
    init_messages()


# Create columns to have party toggle and sidebar switch side by side
col1, col2, col3 = st.columns([1, 1, 1])  # Adjust the ratio as needed for better alignment

with col1:
    # Create a selectbox for the party toggle (Changing value clears history and re-initializes the messages)
    party_toggle = st.selectbox(
        label='Choose party',
        options=['Green Party', 'True Finns'],
        index=0 if st.session_state.party_toggle == 'Green Party' else 1,
        key="party_toggle",
        on_change=init_messages
    )

with col2:
    # Inserting empty header just to align the toggle vertically with the party toggle
    st.header(" ")
    # Toggle for sidebar
    st.toggle('Enable Assistant', 
        value=True, 
        on_change=toggle_sidebar, 
        help="Assistant analyzes the discussion and suggests potential follow-up questions."
    )

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
    
    with st.spinner():
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
        )
        #print(response)
        response_str = f"{response.choices[0].message.content}"        

    #party_avatar = st.image("img/logo_finns_16x16.png")
    #party_avatar = "🌱" if st.session_state.party_toggle == "Green Party" else "🧢"

    # Helper to create a streaming effect
    def stream_data():
        for word in response_str.split(" "):
            yield word + " "
            time.sleep(0.04)

    # Display assistant response in chat message container    
    # with st.chat_message("assistant", avatar=party_avatar):
    with st.chat_message("assistant"):
        st.write_stream(stream_data)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_str})
    
    
#print(st.session_state.messages)

# Play the audio file automatically
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()        
        st.audio(data, autoplay=True)

if st.session_state.sidebar_enabled:
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
        else:
            messages_side.chat_message("assistant", avatar="💡").write('''
            Assistant messages will appear here. 
            
            I will help you by analyzing the responses and suggesting follow-up.                   
            '''
            )
        
    #if prompt := st.chat_input("Something shady going on?"):
    #    messages_side.chat_message("user").write(prompt)
    #    messages_side.chat_message("assistant", avatar="💡").write(f"{prompt}")
