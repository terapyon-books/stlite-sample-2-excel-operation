from io import BytesIO
import streamlit as st
import pandas as pd

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None


@st.cache_data
def get_data(file) -> pd.DataFrame:
    df = pd.read_excel(file)
    return df


st.title("Excelシートの分割・結合")
st.text("Excelファイルのシートのデータを分割したり、結合をします。")

st.header("入力データ")
if st.session_state.uploaded_file is None:
    st.subheader("Excelファイルをアップロードします。")

    uploaded_file = st.file_uploader("Excelファイル", type="xlsx")
    if uploaded_file and st.button("アップロード"):
        st.session_state.uploaded_file = uploaded_file
        st.experimental_rerun()
else:
    st.subheader("アップロード済みのファイル")
    if st.button("ファイルを削除"):
        st.session_state.uploaded_file = None
        st.experimental_rerun()
    df = get_data(st.session_state.uploaded_file)
    st.write(st.session_state.uploaded_file.name)
    st.write(df)

    columns = df.columns.to_list()
    selected_columns = st.selectbox("選択する列", columns)
    if selected_columns:
        # st.write(selected_columns)
        grouped_columns = df.groupby(selected_columns)
        number_of_values = grouped_columns.size()
        st.write(number_of_values)
        for group_name, grouped_df in grouped_columns:
            st.subheader(group_name)
            st.write(grouped_df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for group_name, grouped_df in grouped_columns:
                grouped_df.to_excel(writer, sheet_name=str(group_name))
        output.seek(0)

        st.download_button(
            label="ダウンロード",
            data=output,
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
