import streamlit as st
from sub_word import process_subtitle
import openai
import pysubs2
import tempfile
import os
from pathlib import Path
from utils import lang_list


st.title("字幕生词翻译器")

col1, col2 = st.columns(2)
input_file = col1.file_uploader("上传字幕文件", type=["srt"])
openai_api_key = col2.text_input("OpenAI API Key", type="password")
target_language = col2.selectbox("目标语言", lang_list("simplified chinese"))

if openai_api_key:
    openai.api_key = openai_api_key

difficulty = st.slider("NLTK词频等级，数字越小越难", min_value=1, max_value=50, value=35, step=1)

translate_button = st.button("翻译")
if input_file and translate_button:
    input_subtitle = input_file.read().decode("utf-8")

    temp_input_fd, temp_input_path = tempfile.mkstemp()
    with open(temp_input_path, 'w', encoding="utf-8") as temp_input_file:
        temp_input_file.write(input_subtitle)
    
    input_subs = pysubs2.SSAFile.load(temp_input_path, encoding="utf-8")
    os.close(temp_input_fd)
    os.unlink(temp_input_path)

    # 处理字幕
    with st.spinner("字幕处理中..."):
        output_subs = process_subtitle(input_subs, difficulty, target_language)

    # 获取输入文件的扩展名
    input_file_ext = Path(input_file.name).suffix

    # 创建输出文件的临时文件描述符和路径，使用输入文件的扩展名
    temp_output_fd, temp_output_path = tempfile.mkstemp(suffix=input_file_ext)

    # 保存输出字幕到临时文件
    output_subs.save(temp_output_path, encoding="utf-8")

    # 读取输出字幕文件内容
    with open(temp_output_path, 'r', encoding="utf-8") as output_file:
        output_subtitle = output_file.read()

    # 关闭临时文件描述符并删除临时文件
    os.close(temp_output_fd)
    os.unlink(temp_output_path)

    output_filename = "annotated_"+input_file.name
    # 使用 download_button 提供下载链接
    st.download_button("下载处理后字幕",
                       output_subtitle,
                       output_filename)
