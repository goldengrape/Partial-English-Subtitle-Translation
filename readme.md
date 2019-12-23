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
```python partial_translate_sub.py -i input.srt -o output.srt```

## 致谢
字典来自[ECDICT](https://github.com/skywind3000/ECDICT)