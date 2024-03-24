import streamlit as st

if st.button("シートの分割"):
    st.switch_page("pages/1_split_sheet.py")
if st.button("シートの結合"):
    st.switch_page("pages/2_merge_sheet.py")
