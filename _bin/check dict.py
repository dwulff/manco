# -*- coding: utf-8 -*-
import pandas as pd
import sys

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

counts = pd.read_table('/Users/dwulff/Dropbox (2.0)/Work/Software/pylap/_bin/_dict_components/count_de.txt',header=None)
counts = counts.sort_values(1,ascending=False)
counts.index = range(counts.shape[0])

wolist = pd.read_table('/Users/dwulff/Dropbox (2.0)/Work/Software/pylap/_bin/_dict_components/aspell_de.txt',header=None)[0]
wolist = [wolist[i].lower() for i in range(wolist.shape[0])]

File = open('/Users/dwulff/Dropbox (2.0)/Work/Software/pylap/_cwf/de2.txt','ab')

my_dict = []
for i in range(counts.shape[0]):
    if i % 1000 == 0:
        print i
    wrd = str(counts[0][i]).lower()
    if wrd in wolist:
        wolist.pop(wolist.index(wrd))
        File.write(wrd + '\t' + str(counts[1][i]) + '\n')

for i in range(len(wolist)):
    File.write(wolist[i] + '\t' + str(1) + '\n')

File.close()


word = 'schnapsdrossel'


import re


a = [w for w in wolist if w in word]

filter(re.search,wolist)


'schnaps' in word

re.search('schnaps',word)

r'haus' in wolist

'Haus' in wolist