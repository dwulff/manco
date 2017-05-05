import pandas as pd

counts = pd.read_table('/Users/dwulff/Dropbox (2.0)/Work/Software/pylap/counts/de.txt',header=None)
counts = counts.sort_values(1,ascending=False)
counts.index = range(counts.shape[0])

wolist = pd.read_table('/Users/dwulff/Dropbox (2.0)/Work/Software/pylap/wordlists/de.txt',header=None)[0]
wolist = [wolist[i].lower() for i in range(wolist.shape[0])]

File = open('/Users/dwulff/Dropbox (2.0)/Work/Software/pylap/dictionaries/de.txt','ab')

my_dict = []
for i in range(counts.shape[0]):
    print i
    wrd = str(counts[0][i]).lower()
    if wrd in wolist:
        File.write(wrd + '\t' + str(counts[1][i]) + '\n')

File.close()
