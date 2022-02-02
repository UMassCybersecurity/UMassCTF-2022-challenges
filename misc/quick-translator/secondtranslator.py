#Import libraries
import pandas as pd
import numpy as np
import requests
import time
import random

# languageslist = ["fr", "es", "de", "ga", "vi", "pt"]

languageslist = ["id", "zu", "xh", "sw", "tl"]

#Function to automate translation Yandex taslate
def translate(text, key, language):
    # lang = 'pt'
    url_yandex ="https://translate.yandex.net/api/v1.5/tr.json/translate?key=%s&text=%s&lang=%s" % (key,text,language)
    time.sleep(0.3)
    response = requests.get(url_yandex, timeout=None)
    response_data = eval(response.content.decode('utf-8'))
    lb = response_data['text'][0]
    return lb
 
 
#Test function
key = 'trnsl.1.1.20220126T144721Z.9e05f1f198e22333.aed09042fd6f92d49d529e2e9133e8021ce08d1d' #insert apikey in https://tech.yandex.com/translate/
w = open("translatedwords.txt", "w")
f = open("1000words.csv", "r")
# f = open("testlist.txt", "r")
for word in f:
    randlanguage = languageslist[random.randint(0, 4)]
    # language = "id"
    translation = translate(word, key, randlanguage)
    print(translation)
    w.write("{} ({})\n".format(str(translation).strip("\n"), randlanguage))
    

# text = 'Hola Mundo!'
# print(translate(text, key))
# 'Hello World!'