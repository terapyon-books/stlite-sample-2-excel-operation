from __future__ import annotations
from io import BytesIO
from typing import Literal
import streamlit as st
import pandas as pd

if "uploaded_merge_file" not in st.session_state:
    st.session_state.uploaded_merge_file = None


@st.cache_data
def get_data(file) -> tuple[list[int | str], list[pd.DataFrame]]:
    df = pd.read_excel(file)
    sheet_names = pd.ExcelFile(file).sheet_names
    dfs = []
    for sheet_name in sheet_names:
        df = pd.read_excel(file, sheet_name=sheet_name)
        dfs.append(df)
    return sheet_names, dfs


st.title("Excelシートの結合")
st.text("Excelファイルのシートを結合します。")

st.header("入力データ")
if st.session_state.uploaded_merge_file is None:
    st.subheader("Excelファイルをアップロードします。")

    uploaded_merge_file = st.file_uploader("Excelファイル", type="xlsx")
    if uploaded_merge_file and st.button("アップロード"):
        st.session_state.uploaded_merge_file = uploaded_merge_file
        st.rerun()
else:
    st.subheader("アップロード済みのファイル")
    if st.button("ファイルを削除"):
        st.session_state.uploaded_merge_file = None
        st.rerun()
    sheet_names, temp_dfs = get_data(st.session_state.uploaded_merge_file)
    ignored_sheets = st.multiselect("無視するシート", sheet_names)
    st.write(st.session_state.uploaded_merge_file.name)

    dfs: list[pd.DataFrame] = []
    for sheet_name, temp_df in zip(sheet_names, temp_dfs):
        if sheet_name in ignored_sheets:
            continue
        st.write(sheet_name)
        st.dataframe(temp_df)
        dfs.append(temp_df)

    how = st.selectbox("結合方法", ["縦連結", "横連結", "列指定結合"])
    df: pd.DataFrame | None = None

    if how == "縦連結":
        df = pd.concat(dfs, axis=0, ignore_index=True)
    elif how == "横連結":
        concat_dfs = []
        for i, concat_df in enumerate(dfs):
            concat_df.columns = [f"{col}_{i}" for col in concat_df.columns]
            concat_dfs.append(concat_df)
        join: Literal["inner", "outer"] | None = st.selectbox(
            "結合方法", ["inner", "outer"]
        )
        df = pd.concat(
            concat_dfs,
            axis=1,
            join=join if join is not None else "inner",
        )
    elif how == "列指定結合":
        if len(dfs) != 2:
            st.error("結合するデータフレームが2つである必要があります。")
            st.stop()
        else:
            if st.toggle("ベースのデータフレームを反転"):
                df0 = dfs[1]
                df1 = dfs[0]
            else:
                df0 = dfs[0]
                df1 = dfs[1]
            how_merge: Literal["inner", "outer", "left", "right"] | None = st.selectbox(
                "結合方法", ["inner", "outer", "left", "right"]
            )
            on = st.selectbox("結合キー", dfs[0].columns.to_list())
            df = pd.merge(
                df0,
                df1,
                on=on,
                how=how_merge if how_merge is not None else "inner",
            )
    if df is not None:
        st.dataframe(df)

        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        st.download_button(
            label="ダウンロード",
            data=output,
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
