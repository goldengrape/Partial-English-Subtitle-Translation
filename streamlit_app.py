import streamlit as st
# from argparse import ArgumentParser
from io import StringIO
from sub_word import process_subtitle
import openai 

st.title("字幕生词翻译器")

col1,col2=st.columns(2)
# 上传输入文件
openai_api_key = col2.text_input("OpenAI API Key", type="password")
if openai_api_key:
    openai.api_key = openai_api_key
input_file = col1.file_uploader("上传字幕文件", type=["srt"])

st.markdown("词频等级，数字越小越难")
difficulty = st.slider("词频等级", min_value=1, max_value=50, value=35, step=1)
target_language = st.selectbox("目标语言",["Simplified Chinese"])

translate_button = st.button("翻译")
if input_file and translate_button:
    # input_subtitle = StringIO(input_file.getvalue().decode("utf-8"))
    input_subtitle = input_file.read().decode("utf-8")

    # 处理字幕
    with st.spinner("字幕处理中..."):
        output_subtitle = process_subtitle(input_subtitle, difficulty, target_language)
    # print(output_subtitle)
    output_filename=input_file.name.replace(".srt","_processed.srt")
    # 使用 download_button 提供下载链接
    st.download_button("下载处理后字幕", 
                       output_subtitle, 
                       output_filename)
