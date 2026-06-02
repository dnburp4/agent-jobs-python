import streamlit as st
from Frontend_UI.input_section import render_inputs
from Frontend_UI.progress_section import run_pipeline
from Frontend_UI.results_section import render_results

col1, col2 = st.columns([1, 1], gap="large")
with col1:

    inputs = render_inputs()

    if inputs:
        result = run_pipeline(inputs)
        st.session_state["result"] = result

with col2:

    if "result" in st.session_state:
        render_results(st.session_state["result"])