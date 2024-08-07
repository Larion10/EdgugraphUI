import streamlit as st
import networkx as nx
from pyvis.network import Network
import random
import os

# Function to generate a random color
def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Helper function to create a random graph
def create_random_graph(num_nodes, num_edges):
    G = nx.gnm_random_graph(num_nodes, num_edges)
    for node in G.nodes():
        G.nodes[node]['description'] = f"This is node {node}."
        G.nodes[node]['color'] = get_random_color()
    for edge in G.edges():
        G.edges[edge]['description'] = f"Edge between node {edge[0]} and node {edge[1]}."
        G.edges[edge]['color'] = "#000000"  # Set edge color to black
    return G

# Helper function to draw graph using pyvis
def draw_graph(G):
    net = Network(notebook=True, height="600px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    
    # Add node descriptions to title and colors
    for node in G.nodes(data=True):
        net.get_node(node[0])['title'] = node[1]['description']
        net.get_node(node[0])['label'] = node[1]['description']
        net.get_node(node[0])['color'] = node[1]['color']
    
    # Ensure all edges are black and remove edge titles
    for edge in net.edges:
        edge['color'] = "#000000"

    # Save and return the graph
    path = "graph.html"
    net.show(path)
    return path

# Custom CSS to reduce page margins
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

# Streamlit UI
st.title("Interactive Random Network Graph")

# Add a button to generate a new random graph
if 'graph' not in st.session_state:
    st.session_state['graph'] = None

num_nodes = st.sidebar.slider("Number of Nodes", 5, 50, 10)
num_edges = st.sidebar.slider("Number of Edges", 5, 100, 15)

if st.sidebar.button("Generate Random Graph"):
    st.session_state['graph'] = create_random_graph(num_nodes, num_edges)

G = st.session_state['graph']

if G is not None:
    path = draw_graph(G)

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
