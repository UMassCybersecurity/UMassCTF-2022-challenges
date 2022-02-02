from googletrans import Translator, constants
import googletrans
from pprint import pprint
import random

translator = Translator()

languageslist = ["fr", "es", "de", "ga", "vi", "pt"]
# print(googletrans.LANGUAGES)

correctcount = 0

f = open("1000words.csv", "r")
w = open("translatedwords.txt", "w")
for word in f:
  word = word.strip('\n')
  a = random.randint(0, 5)
  translation = translator.translate(word, dest=languageslist[a])
  print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")


  translateback = translator.translate(translation.text, dest="en")
  if word == translateback.text:
      correctcount += 1

  print(correctcount)

  w.write(translation.text + " " + translation.dest + "\n")



  

# translate a spanish text to english text (by default)
# translation = translator.translate("Hola Mundo")
# print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")