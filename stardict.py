from __future__ import print_function
import sys
import os
import io
import csv
import json 

unicode = str
long = int
xrange = range
def stripword(word):
    return (''.join([ n for n in word if n.isalnum() ])).lower()

#----------------------------------------------------------------------
# CSV COLUMNS
#----------------------------------------------------------------------
COLUMN_SIZE = 13
COLUMN_ID = COLUMN_SIZE
COLUMN_SD = COLUMN_SIZE + 1
COLUMN_SW = COLUMN_SIZE + 2


#----------------------------------------------------------------------
# DictCsv
#----------------------------------------------------------------------
class DictCsv (object):

    def __init__ (self, filename, codec = 'utf-8'):
        self.__csvname = None
        if filename is not None:
            self.__csvname = os.path.abspath(filename)
        self.__codec = codec
        self.__heads = ( 'word', 'phonetic', 'definition', 
            'translation', 'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 
            'exchange', 'detail', 'audio' )
        heads = self.__heads
        self.__fields = tuple([ (heads[i], i) for i in range(len(heads)) ])
        self.__names = {}
        for k, v in self.__fields:
            self.__names[k] = v
        numbers = []
        for name in ('collins', 'oxford', 'bnc', 'frq'):
            numbers.append(self.__names[name])
        self.__numbers = tuple(numbers)
        self.__enable = self.__fields[1:]
        self.__dirty = False
        self.__words = {}
        self.__rows = []
        self.__index = []
        self.__read()

    def reset (self):
        self.__dirty = False
        self.__words = {}
        self.__rows = []
        self.__index = []
        return True

    def encode (self, text):
        if text is None:
            return None
        text = text.replace('\\', '\\\\').replace('\n', '\\n')
        return text.replace('\r', '\\r')

    def decode (self, text):
        output = []
        i = 0
        if text is None:
            return None
        size = len(text)
        while i < size:
            c = text[i]
            if c == '\\':
                c = text[i + 1:i + 2]
                if c == '\\':
                    output.append('\\')
                elif c == 'n':
                    output.append('\n')
                elif c == 'r':
                    output.append('\r')
                else:
                    output.append('\\' + c)
                i += 2
            else:
                output.append(c)
                i += 1
        return ''.join(output)

    # 安全转行整数
    def readint (self, text):
        if text is None:
            return None
        if text == '':
            return 0
        try:
            x = long(text)
        except:
            return 0
        if x < 0x7fffffff:
            return int(x)
        return x

    # 读取文件
    def __read (self):
        self.reset()
        filename = self.__csvname
        if filename is None:
            return False
        if not os.path.exists(self.__csvname):
            return False
        codec = self.__codec
        if sys.version_info[0] < 3:
            fp = open(filename, 'rb')
            content = fp.read()
            if not isinstance(content, type(b'')):
                content = content.encode(codec, 'ignore')
            content = content.replace(b'\r\n', b'\n')
            bio = io.BytesIO()
            bio.write(content)
            bio.seek(0)
            reader = csv.reader(bio)
        else:
            reader = csv.reader(open(filename, encoding = codec))
        rows = []
        index = []
        words = {}
        count = 0
        for row in reader:
            count += 1
            if count == 1:
                continue
            if len(row) < 1:
                continue
            if sys.version_info[0] < 3:
                row = [ n.decode(codec, 'ignore') for n in row ]
            if len(row) < COLUMN_SIZE:
                row.extend([None] * (COLUMN_SIZE - len(row)))
            if len(row) > COLUMN_SIZE:
                row = row[:COLUMN_SIZE]
            word = row[0].lower()
            if word in words:
                continue
            row.extend([0, 0, stripword(row[0])])
            words[word] = 1
            rows.append(row)
            index.append(row)
        self.__rows = rows
        self.__index = index
        self.__rows.sort(key = lambda row: row[0].lower())
        self.__index.sort(key = lambda row: (row[COLUMN_SW], row[0].lower()))
        for index in xrange(len(self.__rows)):
            row = self.__rows[index]
            row[COLUMN_ID] = index
            word = row[0].lower()
            self.__words[word] = row
        for index in xrange(len(self.__index)):
            row = self.__index[index]
            row[COLUMN_SD] = index
        return True

    # 保存文件
    def save (self, filename = None, codec = 'utf-8'):
        if filename is None:
            filename = self.__csvname
        if filename is None:
            return False
        if sys.version_info[0] < 3:
            fp = open(filename, 'wb')
            writer = csv.writer(fp)
        else:
            fp = open(filename, 'w', encoding = codec)
            writer = csv.writer(fp)
        writer.writerow(self.__heads)   
        for row in self.__rows:
            newrow = []
            for n in row:
                if isinstance(n, int) or isinstance(n, long):
                    n = str(n)
                elif not isinstance(n, bytes):
                    if (n is not None) and sys.version_info[0] < 3:
                        n = n.encode(codec, 'ignore')
                newrow.append(n)
            writer.writerow(newrow[:COLUMN_SIZE])
        fp.close()
        return True

    # 对象解码
    def __obj_decode (self, row):
        if row is None:
            return None
        obj = {}
        obj['id'] = row[COLUMN_ID]
        obj['sw'] = row[COLUMN_SW]
        skip = self.__numbers
        for key, index in self.__fields:
            value = row[index]
            if index in skip:
                if value is not None:
                    value = self.readint(value)
            elif key != 'detail':
                value = self.decode(value)
            obj[key] = value
        detail = obj.get('detail', None)
        if detail is not None:
            if detail != '':
                detail = json.loads(detail)
            else:
                detail = None
        obj['detail'] = detail
        return obj

    # 对象编码
    def __obj_encode (self, obj):
        row = [ None for i in xrange(len(self.__fields) + 3) ]
        for name, idx in self.__fields:
            value = obj.get(name, None)
            if value is None:
                continue
            if idx in self.__numbers:
                value = str(value)
            elif name == 'detail':
                value = json.dumps(value, ensure_ascii = False)
            else:
                value = self.encode(value)
            row[idx] = value
        return row

    # 重新排序
    def __resort (self):
        self.__rows.sort(key = lambda row: row[0].lower())
        self.__index.sort(key = lambda row: (row[COLUMN_SW], row[0].lower()))
        for index in xrange(len(self.__rows)):
            row = self.__rows[index]
            row[COLUMN_ID] = index
        for index in xrange(len(self.__index)):
            row = self.__index[index]
            row[COLUMN_SD] = index
        self.__dirty = False

    # 查询单词
    def query (self, key):
        if key is None:
            return None
        if self.__dirty:
            self.__resort()
        if isinstance(key, int) or isinstance(key, long):
            if key < 0 or key >= len(self.__rows):
                return None
            return self.__obj_decode(self.__rows[key])
        row = self.__words.get(key.lower(), None)
        return self.__obj_decode(row)

    # 查询单词匹配
    def match (self, word, count = 10, strip = False):
        if len(self.__rows) == 0:
            return []
        if self.__dirty:
            self.__resort()
        if not strip:
            index = self.__rows
            pos = 0
        else:
            index = self.__index
            pos = COLUMN_SW
        top = 0
        bottom = len(index) - 1
        middle = top
        key = word.lower()
        if strip:
            key = stripword(word)
        while top < bottom:
            middle = (top + bottom) >> 1
            if top == middle or bottom == middle:
                break
            text = index[middle][pos].lower()
            if key == text:
                break
            elif key < text:
                bottom = middle
            elif key > text:
                top = middle
        while index[middle][pos].lower() < key:
            middle += 1
            if middle >= len(index):
                break
        cc = COLUMN_ID
        likely = [ (tx[cc], tx[0]) for tx in index[middle:middle + count] ]
        return likely

    # 批量查询
    def query_batch (self, keys):
        return [ self.query(key) for key in keys ]

    # 单词总量
    def count (self):
        return len(self.__rows)

    # 取得长度
    def __len__ (self):
        return len(self.__rows)

    # 取得单词
    def __getitem__ (self, key):
        return self.query(key)

    # 是否存在
    def __contains__ (self, key):
        return self.__words.__contains__(key.lower())

    # 迭代器
    def __iter__ (self):
        record = []
        for index in xrange(len(self.__rows)):
            record.append((index, self.__rows[index][0]))
        return record.__iter__()

    # 注册新单词
    def register (self, word, items, commit = True):
        if word.lower() in self.__words:
            return False
        row = self.__obj_encode(items)
        row[0] = word
        row[COLUMN_ID] = len(self.__rows)
        row[COLUMN_SD] = len(self.__rows)
        row[COLUMN_SW] = stripword(word)
        self.__rows.append(row)
        self.__index.append(row)
        self.__words[word.lower()] = row
        self.__dirty = True
        return True

    # 删除单词
    def remove (self, key, commit = True):
        if isinstance(key, int) or isinstance(key, long):
            if key < 0 or key >= len(self.__rows):
                return False
            if self.__dirty:
                self.__resort()
            key = self.__rows[key][0]
        row = self.__words.get(key, None)
        if row is None:
            return False
        if len(self.__rows) == 1:
            self.reset()
            return True
        index = row[COLUMN_ID]
        self.__rows[index] = self.__rows[len(self.__rows) - 1]
        self.__rows.pop()
        index = row[COLUMN_SD]
        self.__index[index] = self.__index[len(self.__rows) - 1]
        self.__index.pop()
        del self.__words[key]
        self.__dirty = True
        return True

    # 清空所有
    def delete_all (self, reset_id = False):
        self.reset()
        return True

    # 更改单词
    def update (self, key, items, commit = True):
        if isinstance(key, int) or isinstance(key, long):
            if key < 0 or key >= len(self.__rows):
                return False
            if self.__dirty:
                self.__resort()
            key = self.__rows[key][0]
        key = key.lower()
        row = self.__words.get(key, None)
        if row is None:
            return False
        newrow = self.__obj_encode(items)
        for name, idx in self.__fields:
            if idx == 0:
                continue
            if name in items:
                row[idx] = newrow[idx]
        return True

    # 提交变更
    def commit (self):
        if self.__csvname:
            self.save(self.__csvname, self.__codec)
        return True

    # 取得所有单词
    def dumps (self):
        return [ n for _, n in self.__iter__() ]

