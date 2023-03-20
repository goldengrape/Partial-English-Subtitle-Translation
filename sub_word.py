import openai
import re
import argparse
import os 
import time 
from utils import tokenize_word,is_difficult_word, exclude_words, identify_rare_words,query_gpt3
from utils import parse_json_from_text
import pysubs2
import json 
import tqdm
# import backoff 

def clean_result(result,N=10):
    # 去除括号内的内容
    result = re.sub(r'\([^)]*\)', '', result)
    # 去掉标点和空格
    result = re.sub(r'[\s.,。，！]+', '', result)
    # 如果是x, 如果长度大于N个汉字，或者显示无法翻译，则返回空字符串
    if ((result.lower() == "x") or 
       (len(result) > N) or 
       ("无法翻译" in result)
       ):
        return ""
    return result

def clean_json_result(result):
    # 从result中提取出字典
    dict=parse_json_from_text(result)
    for key in dict.keys():
        dict[key]=clean_result(dict[key])
    return dict

def translate_rare_words_together(words, context, target_language="Chinese"):
    prompt = f"""
    Please give me the MOST APPROPRIATE {target_language} meaning of these words '{words}' IN this sentence: 
    ----
    {context}
    ----
    The response must be in json format, 
    with the keys being the words and the values being the translations.
    The response must be AS CONCISE AS POSSIBLE and NOT include any pinyin.
    The response must NOT contain the translation of entire sentence.
    """
    result = query_gpt3(prompt)
    clean_timer=time.time()
    result=clean_json_result(result)
    # print(f"clean result time: {time.time()-clean_timer}")
    # print(f"Translation of '{words}': {result}")
    # print(f"type of result: {type(result)}")
    return result

def process_subtitle(subs, word_judge, target_language):
    total_lines=len(subs)
    pbar=tqdm.tqdm(total=total_lines)
    for line in subs:
        start_time_line= time.time()

        # 读取字幕，并清洗
        text = line.text
        # 删除\\N
        text = re.sub(r'\\N', ' ', text)
        # print(text)

        # 找出生词
        rare_words = identify_rare_words(text, word_judge)
        
        if len(rare_words) == 0:
            continue
        # print(rare_words)
        
        # 翻译生词
        translation_timer=time.time()
        translations = translate_rare_words_together(rare_words, text, target_language)
        # print(f"Time for translation: {time.time()-translation_timer}")
        
        # 替换文本
        # annotation_timer=time.time()
        annotated_text = text
        for word, translation in translations.items():
            annotated_text = re.sub(
                rf'(?<!\()(\b{word}\b)(?!\))',
                rf'\g<1>({translation})',
                annotated_text,
                flags=re.IGNORECASE
            )
        line.text = annotated_text
        pbar.update(1)

        # print(annotated_text)
        # print(f"Time for annotation: {time.time()-annotation_timer}")

        # print(f"Time for this line: {time.time()-start_time_line}")
    pbar.close()
    return subs


def create_parser():
    parser = argparse.ArgumentParser(description="A subtitle processing program that annotates rare English words with their Chinese translations.")
    parser.add_argument('-i', '--input', dest="input_filename", help="需要处理的英文字幕文件")
    parser.add_argument('-o', '--output', dest="output_filename", help='输出文件')
    parser.add_argument("-d", "--difficulty", dest="difficulty", type=int, help="难度等级, 数字越小越难", default=35)
    parser.add_argument('-t', '--target_language', nargs='?', dest='target_language',
                        type=str, help='目标语言, 默认为中文', default="Simplified Chinese")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    

    input_subs = pysubs2.load(args.input_filename, encoding="utf-8")

    output_subs = process_subtitle(input_subs, args.difficulty, args.target_language)

    output_subs.save(args.output_filename, encoding="utf-8")

    print(f"Processed subtitle saved to {args.output_filename}")

if __name__ == "__main__":  
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    main()
