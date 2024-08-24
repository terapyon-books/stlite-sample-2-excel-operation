from io import BytesIO
import streamlit as st
import pandas as pd


st.title("Excelシートの分割")
st.text("Excelファイルのシートのデータを分割をします。")

st.header("入力データ")
st.subheader("Excelファイルをアップロードします。")

uploaded_split_file = st.file_uploader("Excelファイル", type="xlsx")
if uploaded_split_file:
    st.subheader("アップロード済みのファイル")
    temp_df = pd.read_excel(uploaded_split_file)
    ignored_columns = st.multiselect("無視する列", temp_df.columns.to_list())
    ignored_rows = st.multiselect("無視する行", temp_df.index.to_list())
    if ignored_rows:
        replace_columns = st.toggle("列名を置換する")
    else:
        replace_columns = False
    selected_df = temp_df.drop(ignored_rows, axis=0).drop(ignored_columns, axis=1)
    st.write(uploaded_split_file.name)

    if replace_columns:
        df = selected_df.iloc[1:, :]
        columns_name = selected_df.iloc[0, :]
        if columns_name.notna().all() and all(
            isinstance(name, str) for name in columns_name
        ):
            df.columns = columns_name
    else:
        df = selected_df
    # st.write(df.dtypes)
    st.dataframe(df)  # ここでエラーになるケースがある。原因不明

    columns = df.columns.to_list()
    selected_columns = st.selectbox("選択する列", columns)
    if selected_columns:
        grouped_columns = df.groupby(selected_columns)
        number_of_values = grouped_columns.size()
        st.write(number_of_values)
        has_df = False
        for group_name, grouped_df in grouped_columns:
            st.subheader(group_name)
            st.dataframe(grouped_df)
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
