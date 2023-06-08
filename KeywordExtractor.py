#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this script 
#
# Copyright (C) 2022, Qatar Computing Research Institute, HBKU, Qatar
# Las Update: Thu Sep 29 23:22:45 +03 2022
# Author: Ahmed Abdelali <aabdelali at hbku dot edu do qa>
#
#
# Adapted from: github.com/aneesha/RAKE/rake.py
# http://sujitpal.blogspot.com/2013/03/implementing-rake-algorithm-with-nltk.html
#
from __future__ import division
import operator
import nltk
import string
import json
import requests
import os


def isPunct(word):
  return len(word) == 1 and word in string.punctuation

def isNumeric(word):
  try:
    float(word) if '.' in word else int(word)
    return True
  except ValueError:
    return False

def farasa_POStagger(text):
    '''
    Register to farasa and 
    '''
    url = 'https://farasa.qcri.org/webapi/pos/'
    payload = {'text': text, 'api_key': os.environ["FARASA_API_KEY"],}
    data = requests.post(url, data=payload)
    result = json.loads(data.text)
    #print(result)
    elts = result['text'][1:]
    #print(elts)
    nelts  = []
    newelt = {}
    for elt in elts:
        elt['surface'] = elt['surface'].replace(' ','')
        if(elt['position']=='I'):
            newelt['surface']+=elt['surface']
            newelt['POS']+='+'+elt['POS']
            newelt['num']+=elt['num']
            newelt['position']= 'B'    
        elif(elt['position']=='B'):
            if(newelt!={}):
                nelts.append(newelt)
            newelt = elt

    return nelts

def loadStopwords(filename):
    mylist = []
    for line in open(filename):
        line = line.strip()
        mylist.append(line)
    return mylist

def format_POS_tagged_data(text):
    stopwords = set(loadStopwords('nltk_stopwords_ara.txt')).union(set(nltk.corpus.stopwords.words()))
    all_data = ''
    for t in farasa_POStagger(text):
        if t['surface'].replace('+','') in stopwords or ( 'NOUN' not in t['POS']) or 'PRON' in t['POS'] or 'PREP' in t['POS'] or 'CONJ' in t['POS']: #'V' not in t['POS'] or
            all_data += ' | '
        else:
            all_data += t['surface'].replace('+','')+' ' #+'/'+t['POS']
    return all_data

class RakeKeywordExtractor:

  def __init__(self):
    self.stopwords = set(nltk.corpus.stopwords.words())
    self.stopwords = set(self._loadStopwords('nltk_stopwords_ara.txt')).union(set(nltk.corpus.stopwords.words()))
    self.top_fraction = 1 # consider top third candidate keywords by score

  def _loadStopwords(self,filename):
     mylist = []
     for line in open(filename):
       line = line.strip()
       mylist.append(line)
     return mylist

  def _generate_candidate_keywords(self, sentences):
    phrase_list = []
    for sentence in sentences:
      words = map(lambda x: "|" if x in self.stopwords else x,
        nltk.word_tokenize(sentence.lower()))
      phrase = []
      for word in words:
        if word == "|" or isPunct(word):
          if len(phrase) > 0:
            phrase_list.append(phrase)
            phrase = []
        else:
          phrase.append(word)
    return phrase_list

  def _calculate_word_scores(self, phrase_list):
    word_freq = nltk.FreqDist()
    word_degree = nltk.FreqDist()
    for phrase in phrase_list:
      degree = len(list(filter(lambda x: not isNumeric(x), phrase))) - 1
      for word in phrase:
        word_freq[word] +=1 #word_freq.inc(word)
        word_degree[word] = degree #word_degree.inc(word, degree) # other words
    for word in word_freq.keys():
      word_degree[word] = word_degree[word] + word_freq[word] # itself
    # word score = deg(w) / freq(w)
    word_scores = {}
    for word in word_freq.keys():
      word_scores[word] = word_degree[word] / word_freq[word]
    return word_scores

  def _calculate_phrase_scores(self, phrase_list, word_scores):
    phrase_scores = {}
    for phrase in phrase_list:
      phrase_score = 0
      for word in phrase:
        phrase_score += word_scores[word]
      phrase_scores[" ".join(phrase)] = phrase_score
    return phrase_scores
    
  def extract(self, text, incl_scores=False):
    sentences = nltk.sent_tokenize(text)
    phrase_list = self._generate_candidate_keywords(sentences)
    word_scores = self._calculate_word_scores(phrase_list)
    phrase_scores = self._calculate_phrase_scores(
      phrase_list, word_scores)
    sorted_phrase_scores = sorted(phrase_scores.items(),
      key=operator.itemgetter(1), reverse=True)
    n_phrases = len(sorted_phrase_scores)
    if incl_scores:
      return sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]
    else:
      return map(lambda x: x[0],
        sorted_phrase_scores[0:int(n_phrases/self.top_fraction)])

  def extractArabic(self, text, incl_scores=False):
      return self.extract(format_POS_tagged_data(text),incl_scores)

def test():
  rake = RakeKeywordExtractor()
  keywords = rake.extract("""
Compatibility of systems of linear constraints over the set of natural 
numbers. Criteria of compatibility of a system of linear Diophantine 
equations, strict inequations, and nonstrict inequations are considered. 
Upper bounds for components of a minimal set of solutions and algorithms 
of construction of minimal generating sets of solutions for all types of 
systems are given. These criteria and the corresponding algorithms for 
constructing a minimal supporting set of solutions can be used in solving 
all the considered types of systems and systems of mixed types.
  """, incl_scores=True)
  print(keywords)
  
def testAra():
  rake = RakeKeywordExtractor()
  doc = """جنبلاط: الحكومة اللبنانية ستنفجر عاجلا ام اجلا 
  بيروت 16-8 اف ب قبر  لبنان سياسة 
  اعتبر الزعيم الدرزي وليد جنبلاط ان الحكومة اللبنانية ستنفجر عاجلا ام اجلا بعد الانقلاب الابيض الذي قامت به الاجهزة الامنية والقضائية التي تخضع لوصاية رئيس الجمهورية . 
  وقال جنبلاط في حديث نشرته صحيفة السفير اليوم الخميس ان مجلس الوزراء انتهى بعد ضعف شديد، وليس مقام رئاسة الحكومة الذي تعرض لضربة بل مجلس الوزراء . 
  وكان جنبلاط يعلق بذلك على الاعتقالات الاخيرة التي قامت بها في 5 اب اغسطس اجهزة الاستخبارات في الاوساط المسيحية المعارضة للوجود السوري بدون ابلاغ الحكومة وكذلك على تعديل البرلمان لقانون اعتمد مؤخرا يدعم صلاحيات النيابة. 
  وقال جنبلاط نحن لا نريد تفجير الحكومة اليوم لكن انفجارها سياتي عاجلا ام اجلا . 
  واضاف كنا امام خيارين: اما الاستقالة وتفجير الحكومة والوضع واما الانتظار الى ظروف تجعل خروجنا بالحد الادنى من الكرامة السياسية . وذلك تبريرا لبقاء ثلاثة وزراء يمثلون كتلته النيابية في حكومة رفيق الحريري. 
  وكان الحريري وافق الاثنين مكرها على تعديل قانوني اراده الرئيس اميل لحود. 
  واكد الحريري في البرلمان وسط جلسة صاخبة بان لا احد في البلد يتمنى ان يكون رئيسا للحكومة في هذا الجو . واضاف لكن عدم التصويت سيخلق مشاكل في البلد نحن بغنى عنها في هذا الظرف بالذات لذلك سنمشي بالتعديل . 
  واقر البرلمان الاثنين التعديل بغالبية 70 صوتا من اصل 128 من بينها اصوات كتلة الرئيس الحريري النيابية. 
  وحذر جنبلاط من انه انقلاب ابيض على اتفاق الطائف والدستور قامت به الاجهزة الامنية والقضائية التي تخضع لوصاية رئيس الجمهورية . 
  واضاف ان هؤلاء الاجهزة يخضعون لوصاية رئيس الجمهورية وعندهم استقلالية مالية . 
  وقال ان محصلة ما جرى هو انتصار ادارة امنية وقضائية على السلطتين التشريعية والتنفيذية . واضاف محذرا اننا نسير باتجاه انهيار سياسي سيقود حتما الى انهيار اقتصادي . 
  ومن المقرر ان يشارك جنبلاط في وقت لاحق اليوم في المؤتمر الوطني للحريات العامة الذي ينظمه حزبه وتجمعات ديموقراطية ومسيحية وعلمانية. 
  نحو 50 شخصا يتظاهرون امام بيت الشرق في القدس القدس 16-8 اف ب - تظاهر حوالى خمسين شخصا، فلسطينيون وبضعة اجانب، ظهر اليوم"""
  
  keywords = rake.extractArabic(doc, incl_scores=True)
  print(keywords)

if __name__ == "__main__":
  test()
  testAra()

