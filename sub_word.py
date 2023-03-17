import openai
import re
from collections import defaultdict
from functools import partial
import argparse
import os 
import time 
from stardict import DictCsv

# Set your GPT-3 API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def query_gpt3(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{
        "role": "user", 
        "content": prompt}]
        )
    return response.choices[0].message.content.strip()

def word_unknown(word_query, word_judge):
    if word_query is None:
        return False #查不到就算了 
    
    # 是否认识?
    include_tag=word_judge["include_tag"] 
    exclude_tag=word_judge["exclude_tag"]
    collins_threshold=word_judge["collins_threshold"]; collins_default=True
    bnc_threshold=word_judge["bnc_threshold"]; bnc_default=True
    frq_threshold=word_judge["frq_threshold"]; frq_default=True
    
    # check tag
    include_list=include_tag.lower().split()
    exclude_list=exclude_tag.lower().split()
    if word_query['tag']: # 如果该单词有tag标记
        word_tag=word_query['tag'] 
        tag_chk=(not(any(e in word_tag for e in exclude_list)) 
                 and 
                 any(i in word_tag for i in include_list))    
    else:
        tag_chk=True  #如果该单词没有tag标记, 默认为
    # check collins
    collins_chk = (word_query['collins']<=collins_threshold) if word_query['collins']>=0 else collins_default
    # check bnc
    bnc_chk=(word_query['bnc']>=bnc_threshold) if word_query['bnc']>0 else bnc_default
    # check frq
    frq_chk=(word_query['frq']>=frq_threshold) if word_query['bnc']>0 else frq_default
    # check word length
    length_chk=len(word_query['word']) >= word_judge['word_length']
    return ((tag_chk+collins_chk+bnc_chk+frq_chk) >=3 or length_chk)

def identify_rare_words(text, word_judge):
    words = re.findall(r'\b\w+\b', text)
    sdict=DictCsv("ecdict.csv")
    rare_words=[]
    for word in words:
        if word.isdigit():
            continue
        word_query=sdict.query(word) if sdict.query(word) else sdict.query('unknown')   
        if word_unknown(word_query, word_judge):
            rare_words.append(word)
    return rare_words

def clean_result(result):
    # 如果是x, 如果长度大于6个汉字，或者显示无法翻译，则返回空字符串
    if ((result.lower() == "x") or 
       (len(result) > 10) or 
       ("无法翻译" in result)
       ):
        return ""
    # 去除括号内的内容
    result = re.sub(r'\([^)]*\)', '', result)
    # 去掉标点和空格
    result = re.sub(r'[\s.,。，]+', '', result)
    return result

def translate_word(word, context, target_language="Chinese"):
    prompt = f"""
    Please give me the MOST APPROPRIATE {target_language} meaning of the word '{word}' IN this sentence: 
    ----
    {context}
    ----
    The response must be AS CONCISE AS POSSIBLE and NOT include any pinyin. 
    If unable to translate, please return 'x'.
    """
    try:
        result = query_gpt3(prompt)
    except:
        time.sleep(30)
        result = query_gpt3(prompt)
    result=clean_result(result)
    print(f"Translation of '{word}': {result}")
    return result

def annotate_translation(sentence, translations):
    annotated = sentence
    for word, translation in translations.items():
        # 如果translation为空，则跳过
        if translation == "":
            continue
        annotated = annotated.replace(word, f"{word}({translation})")
    return annotated

def process_subtitle(text,word_judge,target_language):
    rare_words = identify_rare_words(text,word_judge)
    translations = {}
    for word in rare_words:
        for sentence in re.finditer(rf"\b{word}\b", text, flags=re.IGNORECASE):
            context = sentence.group()
            translations[word] = translate_word(word, context, target_language)
    
    annotated_text = text
    for sentence in re.findall(r'(?m)^\d{1,4}\n(?:\d{2}:\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}:\d{2}.\d{3}\n)(.*?)$', text, flags=re.MULTILINE):
        annotated_sentence = annotate_translation(sentence, translations)
        annotated_text = annotated_text.replace(sentence, annotated_sentence)
        print(f"Annotated sentence: {annotated_sentence}")

    return annotated_text

def create_parser():
    parser = argparse.ArgumentParser(description="A subtitle processing program that annotates rare English words with their Chinese translations.")
    parser.add_argument('-i', '--input', dest="input_filename", help="需要处理的英文字幕文件")
    parser.add_argument('-o', '--output', dest="output_filename", help='输出文件')
    parser.add_argument('-include', nargs='?', dest="include_tag", type=str,
                        help='生词的定义: 包含哪些标记, 用空格隔开, 例如 cet6 toelf gre ielts',
                       default="cet6 gre ielts")
    parser.add_argument('-exclude', nargs='?', dest='exclude_tag', type=str,
                        help='生词的定义: 除外哪些标记, 用空格隔开, 例如 zk gk cet4',
                       default="zk gk cet4")
    parser.add_argument('-collins', nargs='?',dest='collins_threshold', type=int, 
                        help='collins星级', default=2)
    parser.add_argument('-bnc', nargs='?', dest='bnc_threshold', type=int,
                       help='英国国家语料库词频顺序bnc, 越大越难', default=5000)
    parser.add_argument('-frq', nargs='?', dest='frq_threshold', type=int,
                       help='当代语料库词频顺序frq, 越大越难', default=5000)
    parser.add_argument('-e', '--exclude_word', nargs='?', dest='exclude_word_filename', 
                        type=str, help='需要排除的单词列表, txt文件, 每行一个单词', 
                        default="exclude_word_list.txt")
    parser.add_argument('-l', '--word_length', nargs='?', dest='word_length', 
                        type=int, help='一定长度以上的单词将默认提示', 
                        default=10)
    parser.add_argument('-t', '--target_language', nargs='?', dest='target_language',
                        type=str, help='目标语言, 默认为中文', default="Simplified Chinese")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    word_judge={}
    word_judge["include_tag"]=args.include_tag 
    word_judge["exclude_tag"]=args.exclude_tag 
    word_judge["collins_threshold"]=args.collins_threshold 
    word_judge["bnc_threshold"]=args.bnc_threshold 
    word_judge['frq_threshold']=args.frq_threshold 
    word_judge['exclude_word_filename']=args.exclude_word_filename
    word_judge['word_length']=args.word_length

    with open(args.input_filename, "r", encoding="utf-8") as f:
        input_subtitle = f.read()

    output_subtitle = process_subtitle(input_subtitle,word_judge,args.target_language)

    with open(args.output_filename, "w", encoding="utf-8") as f:
        f.write(output_subtitle)

    print(f"Processed subtitle saved to {args.output_filename}")

if __name__ == "__main__":
    main()
