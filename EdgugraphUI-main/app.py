import streamlit as st
import networkx as nx
from pyvis.network import Network

from API import api

import random
import asyncio
from io import StringIO
import os
import copy

def create_random_graph(num_nodes=10, num_edges=10):
    G = nx.gnm_random_graph(num_nodes, num_edges)
    for node in G.nodes():
        G.nodes[node]['description'] = f"This is node {node}."
    for edge in G.edges():
        G.edges[edge]['description'] = f"Edge between node {edge[0]} and node {edge[1]}."
        G.edges[edge]['color'] = "#000000"  # Set edge color to black
    return G

# App state
if 'graphs' not in st.session_state:
    st.session_state.graphs = {i: create_random_graph() for i in range(5)}
if 'currentgraph' not in st.session_state:
    st.session_state.currentgraph = None
if 'selected_graphlist' not in st.session_state:
    st.session_state.selected_graphlist = set()
if 'selected' not in st.session_state:
    st.session_state.selected = False
if 'question' not in st.session_state:
    st.session_state.question = ""
if 'answers' not in st.session_state:
    st.session_state.answers = []


def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Functions
def upload_document(uploaded_file, title):
    if uploaded_file is not None:
        st.session_state.graphs[title] = asyncio.run(api.generate_graph([StringIO(uploaded_file.getvalue().decode("utf-8")).read()]))

def draw_graph(G):
    net = Network(notebook=True, height="600px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(copy.deepcopy(G))

    # Add node descriptions to title and colors
    for node in G.nodes(data=True):
        net.get_node(node[0])['title'] = node[1]['description']
        net.get_node(node[0])['label'] = str(node[0])
        net.get_node(node[0])['color'] = get_random_color()

    # Ensure all edges are black and remove edge titles
    for edge in net.edges:
        edge['color'] = "#000000"

    # Save and return the graph
    path = "graph.html"
    net.show(path)
    return path

def ask_question(question):
    return asyncio.run(api.querry(st.session_state.currentgraph, question))

def test():
    question, s_as = asyncio.run(api.question(st.session_state.currentgraph))
    return(question, s_as)

def point(user_answer):
    res = asyncio.run(api.answer_point(
                    st.session_state.question,
                    st.session_state.answers,
                    user_answer
                ))
    return(res)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        color: #333333;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        color: #333333;
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
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# Main layout
st.title("EduGraph")

# Sidebar for Navigation
st.sidebar.header("Navigation")
st.sidebar.image("logo.png", width=150)
page = st.sidebar.radio("Go to", ["Home", "Test", "Understand connections", "Explore the topic", "Create graph", "Browse existing graphs"])

# Content container
with st.container():
    if page == "Home":
        st.header("Welcome to EduGraph!")
        
        st.markdown("""
        To stay at the forefront of innovation, it's essential to evolve education alongside technology. The advent of mobile devices in the early 21st century marked a significant breakthrough in education. Numerous scientifically proven applications now help students deepen their knowledge across various subjects. However, these applications mainly focus on lexical knowledge, whose relevance is diminishing in the AI era. 

        To address this, we introduce a new technology that emphasizes the connections within a topic. EduGraph creates a visual knowledge graph from any written material, such as notes or books, using a large language model (LLM) to detect connections within the document. 

        Our application offers several features to enhance the learning experience. After uploading the material, the generated graph is displayed under the 'Graph' menu, allowing users to explore the connections freely. For deeper understanding, we provide 'Active Revision' and 'Enquiry' features. With Active Revision, the app asks questions about the topic, and users can type in their answers. In the Enquiry tab, users can ask the AI questions to gain a better understanding. 

        These features make EduGraph an excellent tool for personalized learning, complementing traditional education methods. We believe EduGraph will become an indispensable tool for personalized learning experiences.
        """)

    elif page == "Test":
        st.header("Test Page")

        if st.button("Generate Question"):
            with st.spinner('Generating Question... It can take several minutes due to API calls.'):
                st.session_state.question, st.session_state.answers = test()
        
        if st.session_state.question == "":
            st.markdown("No question generated so far")
        else:
            st.markdown(f"Question: {st.session_state.question}")
        
        user_answer = st.text_input("Your Answer")
        if st.button("Submit"):
            if st.session_state.question == "":
                st.markdown("There is no question to be answered.")
            else:
                with st.spinner('Generating points... It can take several minutes due to API calls.'):
                    st.markdown(f"""Your score: {point(user_answer)} / 100""")
                st.markdown("Here are some answers considered perfect:")
                for i in range(3):
                    st.markdown(st.session_state.answers[i])

    elif page == "Understand connections":
        st.header("Understand Connections")
        question = st.text_input("Type your question:")
        if st.button("Send"):
            with st.spinner('Generating answer... It can take several minutes due to API calls.'):
                response = ask_question(question)
            st.markdown(f"**Answer:** {response}")

    elif page == "Explore the topic":
        st.header("Explore the Topic")
        st.write("Feature to be added.")
        st.markdown(
            """
            <style>
            .css-18e3th9 {
                padding: 1rem 1rem 1rem 1rem;  /* Top, Right, Bottom, Left */
            }
            .css-1d391kg {
                padding: 0;  /* Reduce padding around the main container */
            }
            .css-12oz5g7 {
                max-width: 100%;  /* Remove max-width restriction for the main container */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        G = st.session_state.currentgraph

        if G is not None:
            path = draw_graph(G)
            #BUG minidg újragenerálja a plotot, és ronda


            # Create columns for the graph and hover info
            col1, col2 = st.columns([4, 1])  # Adjust the width ratio as needed

            # Display the graph in the first column
            with col1:
                st.write("### Network Graph")
                st.components.v1.html(open(path, 'r').read(), height=600)

            # Display hover info in the second column
            with col2:
                selected_node = st.selectbox("Select a node to see details", list(G.nodes))
                st.write("### Node Description")
                st.write(G.nodes[selected_node]['description'])

                st.write("### Connected Edges")
                for edge in G.edges(selected_node, data=True):
                    st.write(f"{edge}: {edge[2]['description']}")

            # Clean up generated HTML file
            os.remove(path)
        else:
            st.write("Click the button to generate a random graph.")

    elif page == "Create graph":
        st.header("Create Graph")
        title = st.text_input("Title of the graph")
        uploaded_file = st.file_uploader("Upload document", type=["txt"])
        if st.button("Upload"):
            if uploaded_file:
                with st.spinner('Creating the mindmap... It can take several minutes due to API calls.'):
                    upload_document(uploaded_file, title)
            else:
                st.write("No document uploaded")

    elif page == "Browse existing graphs":
        st.header("Browse Existing Graphs")
        if st.button("Clear selection list"):
            st.session_state.selected_graphlist = set()
            st.session_state.currentgraph = None

        if st.session_state.graphs:
            selected_graph = st.selectbox("Select a graph to view", st.session_state.graphs.keys())

            if st.button("Select"):
                #BUG
                st.session_state.selected = True

            if st.session_state.selected:
                st.write(f"Graph {selected_graph} added")
                st.session_state.selected_graphlist.add(selected_graph)                    
                st.write(f"Graph(s) selected:")
                st.write("; ".join([str(s) for s in st.session_state.selected_graphlist]))


                if len(st.session_state.selected_graphlist) == 1:
                    if st.button("Proceed"):
                        st.session_state.currentgraph = st.session_state.graphs[list(st.session_state.selected_graphlist)[0]]
                        st.session_state.selected = False
                else:
                    if st.button("Union"):
                        st.session_state.currentgraph = nx.compose_all([st.session_state.graphs[g] for g in st.session_state.selected_graphlist])
                        st.session_state.selected = False
                    elif st.button("Intersection"):
                        st.session_state.currentgraph = nx.intersection_all([st.session_state.graphs[g] for g in st.session_state.selected_graphlist])
                        st.session_state.selected = False
            else:
                if len(st.session_state.selected_graphlist) > 0:
                    st.write(f"Graph(s) selected:")
                    st.write("; ".join([str(s) for s in st.session_state.selected_graphlist]))

                else:
                    st.write("No Graph(s) selected")
        else:
            st.write("No graphs available.")

if __name__ == "__main__":
    st.experimental_set_query_params(page="Home")
