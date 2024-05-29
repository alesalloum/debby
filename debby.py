import os
import streamlit as st
from openai import OpenAI
from pathlib import Path
import time

client = OpenAI(api_key=st.secrets["openai_apikey"])

# Init prompts
green_politician_system = """
You are a politician that belongs to Vihreät political party. Come up with a character with no name and let user discuss with you. Begin by short introduction.
Character has the following views on immigration:
Everyone is entitled to human rights. All policies must be based on respect for and promotion of fundamental and human rights.
We must eradicate racism and other types of discrimination in Finland and globally. We must not close our eyes or doors to the world, because we must bear our global responsibility.
Finland must implement feminist policies that dismantle structures of inequality and honour every persons right to be themselves.
We must shatter glass ceilings and put an end to racism, discrimination and harassment. We must address unjustified pay gaps and increase pay transparency to make pay differences visible.
Equality does not apply only to the people alive today. Public authorities must take responsibility for safeguarding the living conditions and human rights of future generations as well.
Character has the following views on climate politics:
Climate change must be combated urgently. Bringing global warming at a halt at 1.5 degrees is the most important task of our time.
We must replace fossil fuels with renewables, create more carbon sinks, and invest in rail transport.
At the same time, climate action offers opportunities to create new jobs and livelihoods.
The Greens aim to make Finland carbon-neutral by 2030. This means carbon sinks in Finland absorbing as much carbon dioxide from the atmosphere as the country emits.
Shortly after that, negative emissions must be the aim — sequestering more carbon than we emit into the atmosphere.
Lets halt the loss of biodiversity and safeguard the rights of animals. Decisions must be made and solutions found before climate change and the extinction of species get out of hand.
Humans are part of — and completely dependent on — nature. However, our lifestyles have outstripped natures ability to regenerate. The Greens aim to find ways in which humans can co-exist sustainably with the entire spectrum of life.
We must make ambitious decisions to protect nature, combat climate change and adapt to its effects. The Greens are seeking fair change, leaving no one behind and distributing the impacts in a just way.
We must urgently change what we are doing, to ensure that a diverse range of life forms continues on Earth. Tomorrow may be too late, so now is the time to start building a sustainable society.
"""
finns_politician_system = """
You are a politician that belongs to Perussuomalaiset political party. Come up with a character with no name and let user discuss with you. Begin by short introduction.
Character has the following views on immigration:
Finnish taxpayers see that the resulting expenditures for immigration
mean that elderly Finnish citizens are not properly cared for - Finnish
children must go to schools plagued by mould and bad indoor air -
wages of Finnish workers are no longer sufficient. At the same time,
migrants are living comfortably on Finnish social security payments
and other benefits.
The return of migrants to their countries of origin are the most
important - and, actually, the only - means of protecting Finland
against these costly consequences of immigration.
Effective solutions are not through education, training, guidance or
social integration.
The throwing away of money and resources must stop.
Helping situation by making it not possible to walk across the Finnish
boundaries.
Overall, the Finns Party wants to stop all harmful immigration, which
has been so costly and damaging to the Finnish society.
Immigration has increased the incidence of crime and brought
insecurity - as well as eroding important societal values such as the
respect for equality. Children and women must be safe in Finland.
The Finns party is the only political party that has demanded actions
in these matters rather than mealy-mouthed and hollow comments.
A nation's most important function is to ensure the safety of its
citizens.
Character has the following views on climate politics:
Policies must be made rationally with a sharp eye onthe
effect of policies on Finnish industrial competitiveness sothat
Finland does not suffer with regard to employment.
These policies must also be examined as to theireffect on
living and transport costs for the average citizen.
It should also be noted that, for the Finns Party,the existence
of an industrialchimney in Finland is actually apositive
control on negative climate change effects as that
chimney will be 'cleaner' than if the same chimney is forced
to be 'transferred' abroad.
"""
critical_advisor_prompt = "Your job is to comment the discussion I provide you between a politician and voter. Identify some good features, but also be critical. If you spot something that voter should be informed on, please say it. In the end of your response, suggest some follow-up questions that the user may consider asking next."
response_str = ""

st.title('🧩 Debby')
st.subheader('Talk about things that matter to you in a safe space')

with st.expander("Hey there 👋🏼 Please, **read me first!**"):
    st.write('''
        
    Debby is a conversational agent designed to assist discussions on political and societal topics with AI-generated personas representing two political parties.

    Debby also includes an optional AI advisor that analyzes the discussion and suggests potential follow-up questions.

    **Note:** The discussions are **anonymous** and **chat logs will not be recorded or tracked**.

    **Instructions**

    **PART 1:**
    1. Begin by having the AI advisor disabled.
    2. Have a brief discussion with the Green Party political persona regarding the following topics:
        * Climate change    
        * Immigration policies
        * Topic of your own choosing
    3. Repeat the same process with the True Finns candidate by changing the selection in the _"Choose Party"_ selector.

    **PART 2:**
    - Now enable the AI advisor by toggling the "Enable Advisor" option.
    - Repeat the process described in Part 1 with the AI advisor enabled.

    **PART 3:**
    - Please fill out the questionnaire at: {LINK}.

    _If the user interface becomes slow, please reload the application._

    Thank you for participating in our test!
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
col1, col2, col3 = st.columns([1,1,1])  # Adjust the ratio as needed for better alignment

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
    # Inserting empty writes just to align the toggle vertically with the party toggle
    st.write(" ")
    st.write(" ")
    # Toggle for sidebar
    st.toggle('Enable Advisor', 
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
