这是一个给英文字幕里的生词添加中文翻译注释的小工具. 仍然在改进中

## 使用

1. git clone
```
git clone git@github.com:goldengrape/Partial-English-Subtitle-Translation.git
```

2. 安装pysub2
```pip install pysubs2```

3. 请到[彩云科技开放平台](https://dashboard.caiyunapp.com/user/sign_in/)注册账号，申请开通小译 Token。将Token保存在token.txt文件内.

4. 命令行运行:
* 简单运行, 将input.srt中的生词翻译后输出至output.srt
```python partial_translate_sub.py -i input.srt -o output.srt```
* 自定义“生词”
  * -include 应当包含的标签, 用空格隔开, 例如cet6 toelf gre ielts
  * -exclude 应当除外的标签, 例如zk gk (中考 高考)
  * -collins collins星级, 越小越难
  * -bnc 英国国家语料库词频顺序bnc, 越大越难
  * -frq 当代语料库词频顺序frq, 越大越难
  * -e 需要排除的单词列表, txt文件, 每行一个单词, 可以自行编辑, 默认在exclude_word_list.txt中
  
举例:

```python partial_translate_sub.py -include "cet6 toelf gre ielts" -exclude "zk gk" -collins 2 -bnc 3000 -frq 3000 -i input.srt -o output.srt```

## 致谢
字典来自[ECDICT](https://github.com/skywind3000/ECDICT)