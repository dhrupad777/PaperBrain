import streamlit as st
import tempfile
import json
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.run_pipeline import run_pipeline

st.set_page_config(page_title="Paper Brain ANN", layout="wide")
st.title("Paper Brain — Invoice Intelligence Prototype")

uploaded = st.file_uploader("Upload an invoice PNG", type=["png","jpg","jpeg"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    st.image(tmp_path, caption="Uploaded Invoice", use_container_width=True)

    with st.spinner("Running ANN pipeline..."):
        result = run_pipeline(tmp_path)

    st.subheader("Extracted Fields (BiLSTM-CRF)")
    st.json(result["extracted_fields"])

    if result["anomaly"]:
        st.subheader("Anomaly Detection (Autoencoder)")
        st.json(result["anomaly"])

    st.subheader("Raw Tokens + Tags")
    st.text("\n".join([f"{t}\t{g}" for t,g in zip(result["tokens"], result["tags"])]))
