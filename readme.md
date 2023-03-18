这是一个给英文字幕里的生词添加中文翻译注释的小工具。

# 使用

* 命令行

python sub_word.py -i test/test.srt -o test/output.srt -include "cet6"

* 网页版

https://goldengrape-subword.streamlit.app/



* 自定义“生词”
-include 应当包含的标签, 用空格隔开, 例如cet6 toelf gre ielts
-exclude 应当除外的标签, 例如zk gk (中考 高考)
-collins collins星级, 越小越难
-bnc 英国国家语料库词频顺序bnc, 越大越难
-frq 当代语料库词频顺序frq, 越大越难

# 致谢

字典来自[ECDICT](https://github.com/skywind3000/ECDICT)