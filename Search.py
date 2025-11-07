import streamlit as st

pages = [
    st.Page("search_words.py", title="Search", icon="🔎", default=True),
    st.Page("topic_index.py", title="Topic Index", icon="🗂️"),
    st.Page("glossary.py", title="Glossary", icon="📖"),
    st.Page("model_make.py", title="Model Maker", icon="🛠️"),
    st.Page("view.py", title="Model View", icon="🪟"),
]

pg = st.navigation(pages)
pg.run()
