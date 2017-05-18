import twython
import random
import time
import json

CONSUMER_KEY = '7GUj95HcQJpzUfcb5xLDqJH0Y'
CONSUMER_SECRET = 'jAbYcpDzj4DzX3Djwkum14QPl7r28WoKP3pi6GujkQfR4Ng1SX'
OAUTH_TOKEN = '987662346-pRYKPyjPWfwmXReSgpmGqqZSiFrxNTBfYBY23HLr'
OAUTH_TOKEN_SECRET = 'byucD4exoL7s9uxv8Ef2gur6HZNJYSgTPdNALJvobTIH7'

twitter = twython.Twython(
    CONSUMER_KEY, CONSUMER_SECRET,
    OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

i = 0
tofile = open('/Users/dwulff/Dropbox (2.0)/Work/Teaching/2017 Summer/Naturallanguage/nlpSeminar/twitterSentCorpus.txt','wb')
with open('/Users/dwulff/Downloads/2download/gold/dev/100_topics_100_tweets.sentence-three-point.subtask-A.dev.gold.txt','rb') as File:
    for line in File:
        i += 1
        if i % 10 == 0:
            print i
        d = line.replace('\n','').split('\t')
        try:
            tweet = twitter.show_status(id=d[0].replace('"',''))
            text = tweet['text']
            tofile.write(';'.join(d) + ';' + text + '\n')
            #time.sleep(random.random())
        except:
            print 'somethings wrong'



i = 0
tofile = open('/Users/dwulff/Dropbox (2.0)/Work/Teaching/2017 Summer/Naturallanguage/nlpSeminar/twitterSentCorpus.txt','ab')
with open('/Users/dwulff/nltk_data/corpora/twitter_samples/positive_tweets.json','rb') as File:
    for line in File:
        i += 1
        if i % 10 == 0:
            print i

        tweet = json.loads(line)
        try:
            text = tweet['text']
            tofile.write('positive' + '\t' + text + '\n')
            #time.sleep(random.random())
        except:
            print 'somethings wrong'


tofile.close()