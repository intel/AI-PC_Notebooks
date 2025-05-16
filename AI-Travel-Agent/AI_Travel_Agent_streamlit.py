# Run the file using the below command
# streamlit run AI_Travel_Agent_streamlit.py

# Importing necessary modules
import os
import re
import time
import streamlit as st
from amadeus import Client
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_community.agent_toolkits.amadeus.toolkit import AmadeusToolkit
from langchain_community.tools.amadeus.closest_airport import AmadeusClosestAirport
from langchain_community.tools.amadeus.flight_search import AmadeusFlightSearch
from langchain.agents import AgentExecutor, StructuredChatAgent
from langchain_community.agent_toolkits.load_tools import load_tools

# Loading the secret API keys from a .env file into the environment.
load_dotenv()


@st.cache_resource
def create_llm():
    """
    Create and initialize the LlamaCpp with the selected model.
    Parameters can be changed based on the end user's requirements.
    Here we are using the  Meta Llama 3.1(Q4_K_S) model, which is configured using some hyperparameters.
    For example, GPU Layers are to be offloaded to all the available layers for inference.
    Context Length of 4096 tokens. The temperature is set as 0 for deterministic output.
    Top-P Sampling as 0.95 for controlled randomness, Batch Size as 512 for parallel processing

    Returns:
        LlamaCpp instance for inference.

    Raises:
        Exception: If there is any error during model loading, a Streamlit error is displayed.
    """
    try:
        model_path = hf_hub_download(repo_id="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF", filename="Meta-Llama-3.1-8B-Instruct-Q4_K_S.gguf")  # Downloading the model here

        llm = LlamaCpp(
            # Path to the Llama model file
            model_path=model_path,
            # Number of layers to be loaded into GPU memory (default: 0)
            n_gpu_layers=-1,
            # Random number generator (RNG) seed (default: -1, -1 = random seed)
            seed=512,
            # Token context window (default: 512)
            n_ctx=4096,
            # Use half-precision for key/value cache (default: True)
            f16_kv=True,
            # Pass the callback manager for output handling
            callback_manager=CallbackManager(
                [StreamingStdOutCallbackHandler()]),
            # Print verbose output (default: True)
            verbose=True,
            # Temperature controls the randomness of generated text during sampling (default: 0.8)
            temperature=0,
            # Top-p sampling picks the next token from top choices with a combined probability ≥ p (default: 0.95)
            top_p=0.95,
            # Number of tokens to process in parallel (default: 8)
            n_batch=512,
        )
        # Print verbose state information (default: True). Disabling verbose client output here.
        llm.client.verbose = False

        return llm
    except Exception as e:
        st.error(f"Error loading the model: {e}")


# Tools
def get_google_search_tools():
    """
    Initialize Google search tools for performing web searches.
    Here we are using the GoogleSerperAPIWrapper along with SerpAPI tool.
    It is used perform web searches and retrieve search results.

    Returns:
        list: GoogleSerperAPIWrapper and SerpAPI tools

    Raises:
        Exception: If there is an error during the loading of the Google search tool, a streamlit error is displayed

    """
    try:
        # Initialize the search wrapper to perform Google searches
        search = GoogleSerperAPIWrapper()
        google_search_tool = Tool(
            name="Google Search tool",
            func=search.run,
            description="useful for when you need to ask with search",
        )

        tools = [google_search_tool] + load_tools(["serpapi"])

        return tools
    except Exception as e:
        st.error(f"Error loading the google search tool: {e}")


# Prompt Template

def create_prompt_template():
    """
    The following Prompt template is for the Structured chat agent and is customised to handle the travel related queries.
    """

    PREFIX = """[INST]Respond to the human as helpfully and accurately as possible. You have access to the following tools:"""

    FORMAT_INSTRUCTIONS = """Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

    Use the closest_airport tool and single_flight_search tool for any flight related queries.
    Give all the flight details including Flight Number, Carrier, Departure time, Arrival time and Terminal details to the human.
    Use the Google Search tool and knowledge base for any itinerary-related queries. Give all the detailed information on tourist attractions, must-visit places, and hotels with ratings to the human.
    Use the Google Search tool for distance calculations. Give all the web results to the human.
    Always consider the traveler's preferences, budget constraints, and any specific requirements mentioned in their query.
    Valid "action" values: "Final Answer" or {tool_names}
    Provide only ONE action per $JSON_BLOB, as shown:
    ```
    {{{{
      "action": $TOOL_NAME,
      "action_input": $INPUT
    }}}}
    ```

    Follow this format:

    Question: input question to answer
    Thought: consider previous and subsequent steps
    Action:
    ```
    $JSON_BLOB
    ```
    Observation: action result
    ... (repeat Thought/Action/Observation N times)
    Thought: I know what to respond
    Action:
    ```
    {{{{
      "action": "Final Answer",
      "action_input": "Provide the detailed Final Answer to the human"
    }}}}
    ```[/INST]"""

    SUFFIX = """Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate.
    Format is Action:```$JSON_BLOB```then Observation:.
    Thought:[INST]"""

    HUMAN_MESSAGE_TEMPLATE = "{input}\n\n{agent_scratchpad}"

    return PREFIX, FORMAT_INSTRUCTIONS, SUFFIX, HUMAN_MESSAGE_TEMPLATE


# Agent
def create_agent(llm, tools, PREFIX, SUFFIX, HUMAN_MESSAGE_TEMPLATE, FORMAT_INSTRUCTIONS):
    """
    Create a StructuredChatAgent with llm and tools.
    Initialize a StructuredChatAgent using the LLM, prompt template and tools

    llm : LLM to be used

    tools : list
        List of tools to use

    PREFIX : str
        Prefix string prepended to the agent's input.

    SUFFIX : str
        Suffix string appended to the agent's input.

    HUMAN_MESSAGE_TEMPLATE : str
        Template defining the structure of human messages.

    FORMAT_INSTRUCTIONS : str
        Format instructions for the agent

    Returns:
        StructuredChatAgent configured with LLM and tools.

    Raises:
        Exception : If there is any error during the agent creation, a streamlit error is displayed.
    """
    try:
        agent = StructuredChatAgent.from_llm_and_tools(
            llm,                                            # LLM to use
            tools,                                          # Tools available for the agent
            prefix=PREFIX,                                  # Prefix to prepend to the input
            suffix=SUFFIX,                                  # Suffix to append to the input
            human_message_template=HUMAN_MESSAGE_TEMPLATE,  # Template for human messages
            # Instructions for formatting responses
            format_instructions=FORMAT_INSTRUCTIONS,
        )
        return agent
    except Exception as e:
        st.error(f"Error creating the agent: {e}")


def run_agent(agent, tools):
    """
    Create and configure an AgentExecutor for a structured chat agent with specified tools.

    Initialize a AgentExecutor
    agent : structured chat agent to be used

    tools : list
        List of tools to use by the agent

    verbose : bool
        Used for detailed output

    handle_parsing_errors : bool
        Handle the output parsing-related errors while generating the response

    max_iterations : int
        Used to limit the number of agent iterations to prevent infinite loops.
        Here we are using 1 iteration, We can change based on the requirement.

    early_stopping_method : str
        For stopping the agent execution early.

    Returns:
        AgentExecutor instance for task execution.

    Raises:
        Exception: If there is any error during the agent executor's creation, a streamlit error is displayed
    """
    try:
        agent_executor = AgentExecutor(
            agent=agent,                      # The structured chat agent
            tools=tools,                      # Tools to be used by the agent
            verbose=True,                     # Enable verbose output for debugging
            handle_parsing_errors=True,       # Allow error handling for parsing issues
            # Limit the number of iterations. Can change based on requirement
            max_iterations=1,
            early_stopping_method='generate'  # Method to use for agent early stopping
        )
        return agent_executor
    except Exception as e:
        st.error(f"An error occurred: {e}")


# Streamlit code starts here
# Main title and description
def streamlit_UI():
    """
    Streamlit UI function starts here. Here we are creating a title, header, sidebar with some sample questions.
    The agent excecutor will take the question as input from the streamlit UI, process the output and streams the output response word by word onto the UI.

    Raises:
        Exception: If there is any error during the fetching or streaming the response, a streamlit error is displayed.
    """
    st.title(":earth_africa::airplane: AI Travel Agent")
    st.write("This Langchain-powered AI Travel Agent is designed to assist you with quick travel-related queries. \
    You can request **flight details** for a specific day or find **nearby airports** by location. For other questions, we use **Google Search** for the latest information.")

    # Sidebar with questions on the UI
    st.sidebar.title(":bulb: Example Queries")
    st.sidebar.write("Here are some questions you can ask:")
    predefined_questions = [
        "What are the major airlines that operate to London?",
        "Where is the best place to see the Lantern Festival 2025 in Thailand?",
        "What's the height of the Burj Khalifa in Dubai?",
        "Provide the cheapest flight information to travel from New York to Germany on 15th December 2025.",
        "What are the best places to visit in Spain?"
    ]

    # Store the selected question from sidebar
    selected_sidebar_question = st.sidebar.radio(
        "Choose a Question", predefined_questions)

    # For important notes
    st.markdown("#### **:warning: Important Notes**")
    st.write("""
    - Include your **starting location**, **destination**, and **travel date** when requesting flight details.
    - Always **verify important information**, as the agent may make mistakes.
    """)

    # Additional instruction in a block quote
    st.markdown(
        "> **:notebook: Quick Tip:** Check the **side-bar** for more examples to guide you!")

    # creating columns
    col1, col2 = st.columns([6, 1])

    with col1:
        question = st.text_area(
            "", value=selected_sidebar_question, key="question_input")
    with col2:
        st.write("")
        st.write("")
        st.write("")
        submit = st.button(":mag: Submit")

    if submit:
        if not question.isdigit() and re.search(r'[A-Za-z]', question):
            try:
                with st.spinner("Generating answer..."):
                    with st.expander("Agent Execution", expanded=True):
                        chunks = []
                        for chunk in agent_executor.stream({"input": question}):
                            chunks.append(chunk)
                            st.write(chunk)

                    placeholder = st.empty()
                    content = chunks[2]['output']

                    words = re.split(r'(\s+|\n)', content)

                    accumulated_text = ""

                    for word in words:
                        accumulated_text += word + " "
                        placeholder.write(accumulated_text)
                        time.sleep(0.01)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Invalid question input. Please enter a valid question.")


# calling create_llm function here
llm = create_llm()

# Initialization of amadeus toolkit starts here
try:
    amadeus_client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    amadeus_client_id = os.getenv("AMADEUS_CLIENT_ID")
    amadeus = Client(client_id=amadeus_client_id,
                     client_secret=amadeus_client_secret)
    amadeus_toolkit = AmadeusToolkit(client=amadeus, llm=llm)
    AmadeusToolkit.model_rebuild()
    AmadeusClosestAirport.model_rebuild()
    AmadeusFlightSearch.model_rebuild()

    tools = get_google_search_tools() + amadeus_toolkit.get_tools()

except Exception as e:
    st.error(f"Error loading the amadeus toolkit : {e}")

# calling the create_prompt_template function here
PREFIX, FORMAT_INSTRUCTIONS, SUFFIX, HUMAN_MESSAGE_TEMPLATE = create_prompt_template()

# calling the create_agent function here
try:
    agent = create_agent(llm, tools, PREFIX, SUFFIX,
                         HUMAN_MESSAGE_TEMPLATE, FORMAT_INSTRUCTIONS)
except Exception as e:
    st.error(f"Error loading the agent with tools : {e}")

# calling the run_agent function here
agent_executor = run_agent(agent, tools)

# calling the streamlit_UI function here
streamlit_UI()
