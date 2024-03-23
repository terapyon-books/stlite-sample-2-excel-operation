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
    temp_df = get_data(st.session_state.uploaded_file)
    ignored_columns = st.multiselect("無視する列", temp_df.columns.to_list())
    ignored_rows = st.multiselect("無視する行", temp_df.index.to_list())
    selected_df = temp_df.drop(ignored_rows, axis=0).drop(ignored_columns, axis=1)
    st.write(st.session_state.uploaded_file.name)
    st.write(selected_df)
    
    # df = selected_df.iloc[1:, :]
    columns_name = selected_df.iloc[0, :]
    if not ignored_columns:
        df = selected_df.drop_index()
    if columns_name.notna().all() and all(isinstance(name, str) for name in columns_name):
        df = pd.DataFrame(selected_df.iloc[1:, :].values, columns=columns_name)
    else:
        df = pd.DataFrame(selected_df.iloc[1:, :].values)
    #     df.columns = columns_name
    # df = df.reset_index(drop=True)
    
    st.write(df.dtypes)  # TODO: 選択肢に寄ってエラーになる。
    st.write(df)



    columns = df.columns.to_list()
    selected_columns = st.selectbox("選択する列", columns)
    if selected_columns:
        # st.write(selected_columns)
        grouped_columns = df.groupby(selected_columns)
        number_of_values = grouped_columns.size()
        st.write(number_of_values)
        has_df = False
        for group_name, grouped_df in grouped_columns:
            st.subheader(group_name)
            st.write(grouped_df)
            has_df = True
        if has_df:
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
