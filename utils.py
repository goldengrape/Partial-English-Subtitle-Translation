import nltk
from nltk.corpus import brown

if not nltk.corpus.brown.fileids():
    nltk.download('brown')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

import nltk
from nltk.corpus import brown

if not nltk.corpus.brown.fileids():
    nltk.download('brown')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# 创建基于Brown语料库的词汇频率分布
freq_dist = nltk.FreqDist(w.lower() for w in brown.words())

# 使用nltk进行分词
def tokenize_word(word):
    return nltk.word_tokenize(word)

def is_difficult_word(word, threshold=5):
    tokens = tokenize_word(word)
    for token in tokens:
        if freq_dist[token.lower()] < threshold:
            return True
    return False

exclude_words=set(
    ['updated', 'marginr', 'timing', 'primarycolour', 'scaley', 'name', 'play', 'type', 'encoding', 'scaledborderandshadow', 'strikeout', 'bold', 'styles', 'fontsize', 'wrapstyle', 'fontname', 'outlinecolour', 'alignment', 'italic', 'original', 'update', 'shadow', 'text', 'end', 'underline', 'borderstyle', 'marginl', 'title', 'details', 'timer', 'collisions', 'normal', 'script', 'by', 'point', 'v4', 'start', 'dialogue', 'editing', 'translation', 'defaultarial', 'format', 'backcolour', 'events', 'marginv', 'resx', 'outline', 'default', 'resy', 'synch', 'style', 'scalex', 'effect', 'secondarycolour', 'spacing', 'angle', 'layer',
     'am','is','are','was','were','been','have','has',
     'did','do','does','done','doing','will','would','shall','should','may','might','must','can','could','ought','need','dare','had','having',
     "didn't","doesn't","don't","hadn't","hasn't","haven't","isn't","wasn't","weren't","won't","wouldn't","shan't","shouldn't","can't","cannot","couldn't","mustn't","needn't","oughtn't","daren't","daren't","aren't",
     "didn","doesn","don","hadn","hasn","haven","isn","wasn","weren","won","wouldn","shan","shouldn","can","cannot","couldn","mustn","needn","oughtn","daren","daren","aren",
     'go','goes','going','gone','get','gets','getting','got','gotten',
     'went','come','comes','coming','came',
     ]
    )
