import re
from time import sleep
import numpy.random as random

import html
import urllib.request
import urllib.parse

agent = {
    'User-Agent':
    "Mozilla/4.0 (\
    compatible;\
    MSIE 6.0;\
    Windows NT 5.1;\
    SV1;\
    .NET CLR 1.1.4322;\
    .NET CLR 2.0.50727;\
    .NET CLR 3.0.04506.30\
    )"}

CLASS_SELECTOR = re.compile(r'(?s)class="(?:t0|result-container)">(.*?)<')
BASE_URL = "http://translate.google.com/m?tl={target}&sl={source}&q={text}"

def __translate__(to_translate, to_language='auto', from_language='auto'):
    sleep(random.uniform(.5,.7))
    to_translate = urllib.parse.quote(to_translate)
    link = BASE_URL.format(source=from_language, 
                            target=to_language, 
                            text=to_translate)
    # print(link)
    request = urllib.request.Request(link, headers=agent)
    raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    re_result = CLASS_SELECTOR.findall(data)
    result = '' if not re_result else html.unescape(re_result[0])
    return result

def __call__(to_translate, to_language='auto', from_language='auto'):
    return __translate__(to_translate, to_language, from_language)

def bulk(*strs, 
        input_lang='auto', 
        output_lang='auto', 
        delimiter=";\n") -> list[str]:
    
    s = delimiter.join(strs)
    o = __translate__(s, to_language=input_lang, from_language=output_lang)
    return o.split(delimiter)

import sys

class Module(sys.modules[__name__].__class__):
    def __call__(self, to_translate, to_language='auto', from_language='auto'):
        return __call__(to_translate, to_language, from_language)

sys.modules[__name__].__class__ = Module