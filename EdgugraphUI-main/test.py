import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
from API import api
import asyncio

from io import StringIO

# App state

if 'graphs' not in st.session_state:
    st.session_state.graphs = []
if 'currentgraph' not in st.session_state:
    st.session_state.currentgraph = None

# Generate some random graphs
def generate_random_graphs(num_graphs=5):
    graphs = []
    for i in range(num_graphs):
        G = nx.erdos_renyi_graph(random.randint(5, 15), random.uniform(0.2, 0.5))
    return graphs

# Functions
def upload_document(uploaded_file):
    global graphs
    if uploaded_file is not None:
        st.session_state.graphs.append(asyncio.run(api.generate_graph([StringIO(uploaded_file.getvalue().decode
        ("utf-8")).read()])))
        

    

def ask_question(question):
    return asyncio.run(api.querry(st.session_state.currentgraph, question))

def test():
    return "Sample question?", "Sample answer."



# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        color: #333333;  /* Set default text color to dark */
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        color: #333333;  /* Set sidebar text color to dark */
    }
    .stButton button {
        background-color: #6a11cb;
        color: white;
        border-radius: 10px;
    }
    .stButton button:hover {
        background-color: #2575fc;
        color: white;
    }
    h1, h2, h3 {
        color: #6a11cb;
    }
    .content {
        text-align: center;
    }
    .header-image {
        margin: auto;
        width: 50%;
    }
    .css-1cpxqw2.e1fqkh3o3 {
        color: #333333;  /* Set spinner text color to dark */
    }
    </style>
    """, unsafe_allow_html=True)

# Main layout
st.title("EduGraph")

# Sidebar for Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Test", "Understand connections", "Explore the topic", "Create graph", "Browse existing graphs"])

# Content container
with st.container():
    if page == "Home":
        st.header("Welcome to EduGraph!")
        st.markdown("<div class='content'>Choose an option from the sidebar to get started.</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Test my knowledge!"):
                st.experimental_set_query_params(page="Test")
        with col2:
            if st.button("Understand connections"):
                st.experimental_set_query_params(page="Understand connections")
        with col3:
            if st.button("Explore the topic"):
                st.experimental_set_query_params(page="Explore the topic")
        col4, col5 = st.columns(2)
        with col4:
            if st.button("Create graph"):
                st.experimental_set_query_params(page="Create graph")
        with col5:
            if st.button("Browse existing graphs TBA"):
                st.write("Feature to be added.")

    elif page == "Test":
        st.header("Test Page")
        question, expected_answer = test()
        st.markdown(f"**Question:** {question}")
        user_answer = st.text_input("Your Answer")
        if st.button("Submit"):
            st.markdown(f"**Expected Answer:** {expected_answer}")

    elif page == "Understand connections":
        st.header("Understand Connections")
        question = st.text_input("Type your question:")
        if st.button("Send"):
            response = ask_question(question)
            st.markdown(f"Response: {response}")

    elif page == "Explore the topic":
        st.header("Explore the Topic")
        st.write("Feature to be added.")
        # TODO
        if (st.session_state.currentgraph):
            fig, ax = plt.subplots()
            nx.draw(st.session_state.currentgraph, ax=ax, with_labels=True, node_color='skyblue', node_size=700, edge_color='gray')
            st.pyplot(fig)

    elif page == "Create graph":
        st.header("Create Graph")
        uploaded_file = st.file_uploader("Upload document", type=["txt"])
        if st.button("Upload"):
            if uploaded_file:
                with st.spinner('Creating the mindmap...'):
                    progress_bar = st.progress(0)
                    upload_document(uploaded_file)
                    
            else:
                st.write("No document uploaded")

    elif page == "Browse existing graphs":
        st.header("Browse Existing Graphs")
        if st.session_state.graphs:
            selected_graph = st.selectbox("Select a graph to view", range(len(st.session_state["graphs"])))
            st.session_state.currentgraph = st.session_state["graphs"][selected_graph]

            st.write(f"Graph {selected_graph + 1} selected as current graph.")

            

        else:
            st.write("No graphs available.")

if __name__ == "__main__":
    st.experimental_set_query_params(page="Home")
