# Prompt for GPT-4

* [sub_word.py](sub_word.py)

实现一个用Python编写的字幕处理程序，具备以下功能：

能够识别英文字幕中的生僻单词。
使用GPT-3 API找到生僻单词在句子上下文中的中文意思。
将中文意思标注在英文单词的后面。
采用函数式编程风格，使程序结构化、易于并行化。
能够处理多义词，根据上下文提供更准确的翻译。

* [ingest_dict.py](ingest_dict.py)

写一个python程序，用pandas读取一个csv文件，
该文件有如下字段：
字段	解释
word	单词名称
phonetic	音标，以英语英标为主
definition	单词释义（英文），每行一个释义
translation	单词释义（中文），每行一个释义
pos	词语位置，用 "/" 分割不同位置
collins	柯林斯星级
oxford	是否是牛津三千核心词汇
tag	字符串标签：zk/中考，gk/高考，cet4/四级 等等标签，空格分割
bnc	英国国家语料库词频顺序
frq	当代语料库词频顺序
exchange	时态复数等变换，使用 "/" 分割不同项目，见后面表格
detail	json 扩展信息，字典形式保存例句（待添加）
audio	读音音频 url （待添加）

使用OpenAI的ada模型对其word字段的每一行进行embedding，
这里有一个使用text-similarity-davinci-001模型的例子供参考：
response = openai.Embedding.create(
    input="canine companions say",
    engine="text-similarity-davinci-001")
将embedding的结果与collins,oxford,tag,frq字段合并存储进一个Pandas Dataframe并使用pandas的to_pickle来保存。
要求代码简洁、结构化、以函数式编程风格撰写，最终以main()调用