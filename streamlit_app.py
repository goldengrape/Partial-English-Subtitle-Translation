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

st.markdown("生词判定参数")
col11,col12=st.columns(2)
# 接收用户输入的参数
include_tag = col11.multiselect("包含标签",
            ["cet4","cet6","gre","ielts","toefl","zk","gk"],
            default=["cet6","gre","ielts"])
exclude_tag = col12.multiselect("排除标签",
            ["cet4","cet6","gre","ielts","toefl","zk","gk"],
            default=["zk","gk","cet4"])
col21,col22,col23,col24=st.columns(4)
collins_threshold = col21.number_input("柯林斯星级", value=2)
bnc_threshold = col22.number_input("英国词频顺序", value=5000)
frq_threshold = col23.number_input("当代词频顺序", value=5000)
word_length = col24.number_input("单词长度", value=10)
target_language = st.selectbox("目标语言",["Simplified Chinese"])

translate_button = st.button("翻译")
if input_file and translate_button:
    # input_subtitle = StringIO(input_file.getvalue().decode("utf-8"))
    input_subtitle = input_file.read().decode("utf-8")

    # 创建一个字典，将用户输入的参数存储在其中
    word_judge = {
        "include_tag": " ".join(include_tag),
        "exclude_tag": " ".join(exclude_tag),
        "collins_threshold": collins_threshold,
        "bnc_threshold": bnc_threshold,
        "frq_threshold": frq_threshold,
        "word_length": word_length
    }

    # 处理字幕
    with st.spinner("字幕处理中..."):
        output_subtitle = process_subtitle(input_subtitle, word_judge, target_language)
    # print(output_subtitle)
    output_filename=input_file.name.replace(".srt","_processed.srt")
    # 使用 download_button 提供下载链接
    st.download_button("下载处理后字幕", 
                       output_subtitle, 
                       output_filename)
