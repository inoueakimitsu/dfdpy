import streamlit as st
import streamlit_mermaid as stmd
from streamlit_monaco import st_monaco

from dfdpy.python import make_dfd, MermaidJsGraphExporter

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title("Python Code to DFD Converter")

st.sidebar.header("Python Code to DFD")
st.sidebar.write("This program converts Python source code into a Data Flow Diagram (DFD).")

graph_orientation = st.sidebar.selectbox(
    "Graph Orientation",
    ("TD (Top to Down)", "LR (Left to Right)")
)

if graph_orientation == "LR (Left to Right)":
    graph_orientation = "LR"
else:
    graph_orientation = "TD"

hidden_identifier_list_str = st.sidebar.text_area(
    "Hidden Identifier List", 
    value="np\npd", 
    height=200
)

hidden_identifier_list = [
    item.strip() for item in hidden_identifier_list_str.split('\n') if item.strip()]

source_code = st_monaco(
    value="# write Python code here (Please trim tabs)", language="python", height="300px", lineNumbers=True, minimap=True)

process_node_list, data_store_node_list, edges = make_dfd(
    source=source_code, hidden_id_list=hidden_identifier_list)
exporter = MermaidJsGraphExporter(graph_orientation=graph_orientation)
mermaid_code: str = exporter.export(
    process_node_list=process_node_list, data_store_node_list=data_store_node_list, edges=edges)

stmd.st_mermaid(mermaid_code, height="2000px")
