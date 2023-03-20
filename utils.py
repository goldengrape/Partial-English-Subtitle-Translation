import nltk
from nltk.corpus import brown
import time 
import openai
import re 
import json

def init_nltk():
    if not nltk.corpus.brown.fileids():
        nltk.download('brown')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

# 创建基于Brown语料库的词汇频率分布
init_nltk()
# nltk.download() 
freq_dist = nltk.FreqDist(w.lower() for w in brown.words())

# 使用nltk进行分词
def tokenize_word(word):
    return nltk.word_tokenize(word)

def is_difficult_word(word, threshold=5):
    # tokens = tokenize_word(word)
    # for token in tokens:
    #     if freq_dist[token.lower()] < threshold:
    #         return True
    # return False
    return freq_dist[word.lower()] < threshold

def identify_rare_words(text, threshold):
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
        if is_difficult_word(word,threshold):
            rare_words.append(word)
    return rare_words

sleep_time=60 
def query_gpt3(prompt,cooldown_time=3):
    global sleep_time
    while True:
        try:
            # start_time=time.time()
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=[{
                "role": "user", 
                "content": prompt}]
                )
            # print(f"GPT-3 API time: {time.time()-start_time}")
            answer=response.choices[0].message.content.strip()
            time.sleep(cooldown_time)
            # print(f"after sleep 3s, I finished")
            sleep_time = int(sleep_time/2)
            sleep_time = max(sleep_time, 10)
            break
        except:
            print(f"API error, retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
            sleep_time += 10
            if sleep_time > 120:
                print("API error, aborting...")
                answer=""
                break
    # print(f"Answer: {answer}")
    return answer

def parse_json_from_text(text):
    # 使用正则表达式匹配 JSON 字符串
    match = re.search(r'{[^{}]*}', text, re.DOTALL)

    if match:
        # 提取 JSON 字符串部分
        json_str = match.group()

        # 解析 JSON 字符串成 Python 字典
        try:
            data = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            print('JSON 字符串解析失败')
            return {"":""}
        return data
    else:
        print('未找到 JSON 字符串')
        return {"":""}


exclude_words=set(
    ['updated', 'marginr', 'timing', 'primarycolour', 'scaley', 'name', 'play', 'type', 'encoding', 'scaledborderandshadow', 'strikeout', 'bold', 'styles', 'fontsize', 'wrapstyle', 'fontname', 'outlinecolour', 'alignment', 'italic', 'original', 'update', 'shadow', 'text', 'end', 'underline', 'borderstyle', 'marginl', 'title', 'details', 'timer', 'collisions', 'normal', 'script', 'by', 'point', 'v4', 'start', 'dialogue', 'editing', 'translation', 'defaultarial', 'format', 'backcolour', 'events', 'marginv', 'resx', 'outline', 'default', 'resy', 'synch', 'style', 'scalex', 'effect', 'secondarycolour', 'spacing', 'angle', 'layer',
     'am','is','are','was','were','been','have','has',
     'did','do','does','done','doing','will','would','shall','should','may','might','must','can','could','ought','need','dare','had','having',
     "didn't","doesn't","don't","hadn't","hasn't","haven't","isn't","wasn't","weren't","won't","wouldn't","shan't","shouldn't","can't","cannot","couldn't","mustn't","needn't","oughtn't","daren't","daren't","aren't",
     "didn","doesn","don","hadn","hasn","haven","isn","wasn","weren","won","wouldn","shan","shouldn","can","cannot","couldn","mustn","needn","oughtn","daren","daren","aren",
     'go','goes','going','gone','get','gets','getting','got','gotten',
     'went','come','comes','coming','came',
     'fnMicrosoft', 'YaHei',
     'wan','gon',
     'fuck'
     ]
    )

def lang_list(default_lang):
    l_list=["english",
        "simplified chinese",
        "traditional chinese",
        "german",
        "spanish",
        "russian",
        "korean",
        "french",
        "japanese",
        "portuguese",
        "turkish",
        "polish",
        "catalan",
        "dutch",
        "arabic",
        "swedish",
        "italian",
        "indonesian",
        "hindi",
        "finnish",
        "vietnamese",
        "hebrew",
        "ukrainian",
        "greek",
        "malay",
        "czech",
        "romanian",
        "danish",
        "hungarian",
        "tamil",
        "norwegian",
        "thai",
        "urdu",
        "croatian",
        "bulgarian",
        "lithuanian",
        "latin",
        "maori",
        "malayalam",
        "welsh",
        "slovak",
        "telugu",
        "persian",
        "latvian",
        "bengali",
        "serbian",
        "azerbaijani",
        "slovenian",
        "kannada",
        "estonian",
        "macedonian",
        "breton",
        "basque",
        "icelandic",
        "armenian",
        "nepali",
        "mongolian",
        "bosnian",
        "kazakh",
        "albanian",
        "swahili",
        "galician",
        "marathi",
        "punjabi",
        "sinhala",
        "khmer",
        "shona",
        "yoruba",
        "somali",
        "afrikaans",
        "occitan",
        "georgian",
        "belarusian",
        "tajik",
        "sindhi",
        "gujarati",
        "amharic",
        "yiddish",
        "lao",
        "uzbek",
        "faroese",
        "haitian creole",
        "pashto",
        "turkmen",
        "nynorsk",
        "maltese",
        "sanskrit",
        "luxembourgish",
        "myanmar",
        "tibetan",
        "tagalog",
        "malagasy",
        "assamese",
        "tatar",
        "hawaiian",
        "lingala",
        "hausa",
        "bashkir",
        "javanese",
        "sundanese"]    
    # 将default_lang放在第一位
    l_list.remove(default_lang)
    l_list.insert(0,default_lang)
    return l_list
