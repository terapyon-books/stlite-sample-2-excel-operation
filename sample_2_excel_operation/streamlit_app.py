import streamlit as st

st.title("Excelシートの分割・結合")
st.text("Excelファイルのシートのデータを分割や結合ができます。いずれかのボタンを押してください。")

if st.button("シートの分割"):
    st.switch_page("pages/1_split_sheet.py")
if st.button("シートの結合"):
    st.switch_page("pages/2_merge_sheet.py")
