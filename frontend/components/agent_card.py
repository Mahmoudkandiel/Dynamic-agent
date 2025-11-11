import streamlit as st

def agent_card_grid(agents, on_chat, on_edit, on_delete, cards_per_row=4):
    # 1. Inject the CSS
    st.markdown("""
        <style>
        .agent-grid-container {
            display: flex;
            flex-wrap: wrap;
            gap: 2rem; /* Spacing between cards */
            justify-content: flex-start;
        }

        /* Use Streamlit's container classes to apply card styles */
        /* This targets the column/container surrounding the content */
        .st-emotion-cache-1jm6e3x, .st-emotion-cache-uf99v8, .st-emotion-cache-1jm6e3x > div, .st-emotion-cache-uf99v8 > div { 
            /* Targeting complex Streamlit container/column classes. 
               These are subject to change, but usually work to style the card boundary. */
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 0.8rem 1rem;
            background-color: #ffffff; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.2s ease-in-out;
            min-height: 180px; /* Set a fixed height for consistency */
            margin-bottom: 0px !important; /* Remove bottom margin from the column */
        }
        
        /* Hover effect on the card container */
        .st-emotion-cache-1jm6e3x:hover, .st-emotion-cache-uf99v8:hover {
            border-color: #cfcfcf; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
            transform: translateY(-1px);
        }
        
        /* Style for the card content (text/model info) */
        .card-content h4 {
            font-size: 1.05rem;
            margin-bottom: 0.1rem;
            color: #1f77b4; 
        }

        .card-content p {
            font-size: 0.85rem;
            color: #555;
            margin: 0;
            line-height: 1.3;
        }
        
        /* Styling the Streamlit buttons to be compact */
        .stButton button {
            height: 28px !important;
            padding: 0 8px !important;
            font-size: 0.75rem !important;
            margin: 0 !important;
            border-radius: 8px !important;
        }
        
        /* Adjust column padding to bring buttons closer to the content */
        .st-emotion-cache-p2x35x { /* Targets the columns holding the buttons */
            padding-top: 0.5rem; 
            padding-bottom: 0rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Calculate the number of rows needed
    num_agents = len(agents)
    
    # We will use st.columns to create the grid layout
    
    for i in range(0, num_agents, cards_per_row):
        # Create a row of columns
        cols = st.columns(cards_per_row)
        
        # Iterate over the agents for the current row
        for j in range(cards_per_row):
            agent_index = i + j
            if agent_index < num_agents:
                agent = agents[agent_index]
                
                # 2. Use the column as the card container
                with cols[j]:
                    # Extract Data
                    agent_id = agent.get("_id") or agent.get("id") or agent.get("agent_id")
                    name = agent.get("name", "Unnamed Agent")
                    desc = agent.get("description", "No description")
                    model = agent.get("config", {}).get("model", "N/A")
                    
                    # 3. Create the Card Content HTML
                    # All non-interactive content goes here
                    card_content = f"""
                        <div class="card-content">
                            <h4>🤖 {name}</h4>
                            <p style="font-weight: bold; margin-bottom: 0.2rem;">Model: {model}</p>
                            <p>{desc}</p>
                        </div>
                        """
                    
                    # 4. Render the Card HTML Content
                    st.markdown(card_content, unsafe_allow_html=True)
                    
                    # Add space between content and buttons
                    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

                    # 5. Render Streamlit Buttons *Inside* the Card's Column
                    # Create columns for the buttons within the main grid column
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    
                    with btn_col1:
                        if st.button("💬 Chat", key=f"chat_{agent}"):
                            on_chat(agent)
                    with btn_col2:
                        if st.button("✏️ Edit", key=f"edit_{agent_id}"):
                            on_edit(agent)
                    with btn_col3:
                        if st.button("🗑️ Del", key=f"delete_{agent_id}"): # Using "Del" for space
                            on_delete(agent)
            
        # Optional: Add a small separator after each row of cards if needed, but the gap in CSS should be enough
        # st.markdown("<br>", unsafe_allow_html=True)