

### German

require(rvest)
require(magrittr)
require(stringi)

urls = c('https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-1-5000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-5001-10000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-10001-15000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-15001-20000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-20001-25000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-25001-30000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-30001-35000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-35001-40000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-40001-45000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-45001-50000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-50001-55000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-55001-60000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-60001-65000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-65001-70000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-70001-75000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-75001-80000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-80001-85000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-85001-90000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-90001-95000',
         'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/German_frequency_list-95001-100000')

cnts = ''

for(url in urls){
  html = read_html(url)
  cnt  = html %>% html_node(xpath = '//*[@id="mw-content-text"]/p') %>% html_text()
  cnts = paste(cnts,cnt,sep=' ')
  }

counts = stri_split_fixed(cnts,' ')[[1]]
counts = counts[-c(1,4234:4238)]

options(stringsAsFactors = F)

cnt_dict = data.frame('word'=tolower(counts[seq(2,length(counts),2)]),
                      'count'=as.numeric(counts[seq(1,length(counts),2)]))

unis = unique(cnt_dict$word)

dict = matrix(NA,nrow = length(unis),ncol=2)
for(i in 1:length(unis)){
  if(i %% 100 == 0) print(round(i / length(unis),4)*100)
  word = unis[i]
  cnt = sum(cnt_dict$count[cnt_dict$word == word])
  dict[i,] = c(word,cnt)
  }

text = apply(dict,1,paste,collapse='\t')
con = file('/Users/wulff/Dropbox (2.0)/Work/Software/pylap/dictionaries/de.txt','wb')
writeLines(text,con)
close(con)


#a = stri_detect_regex(counts, pattern = '[0-9]')
#which(a[-1] == a[-length(a)])






