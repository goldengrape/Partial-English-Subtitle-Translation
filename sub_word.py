import openai
import re
import argparse
import os 
import time 
from utils import tokenize_word,is_difficult_word, exclude_words
import pysubs2


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
    # words = re.findall(r'\b\w+\b', text)
    words=tokenize_word(text)
    rare_words=[]
    for word in words:
        if ((word.lower() in exclude_words) or
            (len(word)<=2) or 
            # 如果包含有数字
            (any(char.isdigit() for char in word)) or
            # 如果包含有特殊字符
            (any(not char.isalnum() for char in word)) 
            ):
            continue
        if is_difficult_word(word,word_judge):
            rare_words.append(word)
    return rare_words

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

def translate_word(word, context, target_language="Chinese"):
    prompt = f"""
    Please give me the MOST APPROPRIATE {target_language} meaning of the word '{word}' IN this sentence: 
    ----
    {context}
    ----
    The response must be AS CONCISE AS POSSIBLE and NOT include any pinyin. 
    The response must be in the form of a single word or a short phrase.
    The response must be in {target_language}.
    The response must only be the meaning of the word in the sentence, not the entire sentence's meaning.
    If unable to translate, please return 'x'.
    """
    try:
        result = query_gpt3(prompt)
    except:
        print("GPT-3 API error, retrying in 30 seconds...")
        time.sleep(30)
        result = query_gpt3(prompt)
    result=clean_result(result)
    # print(f"Translation of '{word}': {result}")
    return result

def process_subtitle(subs, word_judge, target_language):
    for line in subs:
        text = line.text
        # 删除\\N
        text = re.sub(r'\\N', ' ', text)
        print(text)
        rare_words = identify_rare_words(text, word_judge)
        if len(rare_words) == 0:
            continue
        print(rare_words)
        annotated_text = text
        for word in rare_words:
            # word_but_no_translate = rf'^(?=.*\b{word}\b)(?!.*\b{word}\().*$'
            for i in range(5):
                sentences_with_word_but_no_translate = re.findall(
                    rf'.*{word}[^\(]+.*', annotated_text, flags=re.IGNORECASE)
                if len(sentences_with_word_but_no_translate) == 0:
                    break
                sentence = sentences_with_word_but_no_translate[0]
                translation = translate_word(word, sentence, target_language)
                if translation == "":
                    continue
                annotated_sentence = sentence
                annotated_sentence = annotated_sentence.replace(
                    word, f"{word}({translation})")
                annotated_text = annotated_text.replace(
                    sentence, annotated_sentence)

        line.text = annotated_text
        print(annotated_text)

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
    # Set your GPT-3 API key
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    main()
