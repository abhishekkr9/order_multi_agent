\
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from graph import app # Import the compiled graph

st.title("Multi-Agent Customer Support Assistant")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask about orders, support, or general info:"):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare input for the graph
    graph_input = {"messages": [HumanMessage(content=prompt)]}

    # Stream the graph execution
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        final_state_messages = []

        # Use a spinner while the agent is thinking
        with st.spinner("Assistant is thinking..."):
            events = app.stream(graph_input, stream_mode="values")
            for event in events:
                if "messages" in event:
                    # Keep track of the latest message list
                    final_state_messages = event["messages"]
                    # Find the last relevant message to display during streaming
                    # Look backwards for the last message not from supervisor or validator
                    display_message = ""
                    for msg in reversed(final_state_messages):
                        # Check if the message has a 'name' attribute and if it's not from internal nodes
                        if isinstance(msg, BaseMessage) and hasattr(msg, 'name') and msg.name not in ["supervisor", "validator"]:
                             # Also check if it's not the initial user message if it's the only one left
                             if len(final_state_messages) > 1 or msg.type != 'human':
                                display_message = msg.content
                                break
                        # Fallback for messages without a name (like initial user message or potentially others)
                        elif isinstance(msg, BaseMessage) and not hasattr(msg, 'name'):
                             # Avoid showing the initial user prompt as the response
                             if len(final_state_messages) > 1 or msg.type != 'human':
                                display_message = msg.content
                                break


                    if display_message:
                         message_placeholder.markdown(display_message + "▌") # Add cursor effect


        # After streaming, determine the definitive final response
        final_response = ""
        if final_state_messages:
             for msg in reversed(final_state_messages):
                 if isinstance(msg, BaseMessage) and hasattr(msg, 'name') and msg.name not in ["supervisor", "validator"]:
                     if len(final_state_messages) > 1 or msg.type != 'human':
                          final_response = msg.content
                          break
                 elif isinstance(msg, BaseMessage) and not hasattr(msg, 'name'):
                      if len(final_state_messages) > 1 or msg.type != 'human':
                           final_response = msg.content
                           break


        # Display the final response without the cursor
        if final_response:
            message_placeholder.markdown(final_response)
        else:
            # Handle cases where no suitable message was found (e.g., only user message exists)
            message_placeholder.markdown("Sorry, I couldn't generate a response.")


    # Add the final assistant response to session state
    if final_response:
        st.session_state.messages.append({"role": "assistant", "content": final_response})

# Add a button to clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
