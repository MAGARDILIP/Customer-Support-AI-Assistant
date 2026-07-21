"""
Upload Documents Page — PDF upload and knowledge base management.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.utils.api_client import upload_document, list_documents, delete_document

st.set_page_config(page_title="Upload Documents - ShopEase", page_icon="📄", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .upload-header {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #1a202c;
    }
    .upload-header h2 { color: #1a202c !important; margin: 0; }
    .upload-header p { color: rgba(26,32,44,0.7); margin: 0; font-size: 0.9rem; }
    .doc-card {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="upload-header">
    <h2>📄 Document Management</h2>
    <p>Upload PDF policies, FAQs, and guides to build the AI's knowledge base</p>
</div>
""", unsafe_allow_html=True)

# --- Upload Section ---
st.subheader("📤 Upload New Document")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload company policies, FAQs, or product guides. The AI will use these to answer customer questions.",
)

if uploaded_file is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"📎 **{uploaded_file.name}** — {uploaded_file.size / 1024:.1f} KB")
    with col2:
        if st.button("🚀 Process & Upload", type="primary", use_container_width=True):
            with st.spinner("Processing PDF... Extracting text, creating embeddings..."):
                result = upload_document(uploaded_file.getvalue(), uploaded_file.name)

            if "error" in result:
                st.error(f"❌ Upload failed: {result['error']}")
            else:
                st.success(
                    f"✅ **{result.get('filename', 'Document')}** uploaded successfully!\n\n"
                    f"- **Document ID:** `{result.get('doc_id', 'N/A')}`\n"
                    f"- **Chunks Created:** {result.get('chunks_created', 0)}"
                )
                st.balloons()

st.markdown("---")

# --- Current Documents ---
st.subheader("📚 Knowledge Base Documents")

docs_data = list_documents()

if "error" in docs_data:
    st.error(f"⚠️ Could not load documents: {docs_data['error']}")
elif docs_data.get("documents"):
    total_chunks = docs_data.get("total_chunks", 0)
    st.metric("Total Knowledge Chunks", total_chunks)
    st.markdown("")

    for doc in docs_data["documents"]:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.markdown(f"📄 **{doc.get('source', 'Unknown')}**")
        with col2:
            st.markdown(f"🧩 {doc.get('chunk_count', 0)} chunks")
        with col3:
            if st.button("🗑️", key=f"del_{doc['doc_id']}", help="Delete this document"):
                result = delete_document(doc["doc_id"])
                if "error" not in result:
                    st.success(f"Deleted {doc.get('source', 'document')}")
                    st.rerun()
                else:
                    st.error(f"Failed to delete: {result['error']}")
else:
    st.info("📭 No documents uploaded yet. Upload a PDF to get started!")

st.markdown("---")

# --- Tips ---
st.subheader("💡 Tips")
st.markdown("""
- **Upload company policies** (return policy, shipping, warranty) to help the AI answer policy questions
- **Upload FAQs** so the AI can handle common questions automatically
- **Upload product guides** for product-specific customer queries
- Documents are split into chunks and stored as embeddings for fast semantic search
- The AI automatically searches these documents when answering customer questions
""")
