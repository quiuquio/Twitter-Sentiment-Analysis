# -*- encoding: utf-8 -*-
#import regex
import re
import csv
import codecs
 
#start process_tweet
def processTweet(tweet):
    # process the tweets
 
    #Minuscole
    tweet = tweet.lower()
    #Converte www.* o https?://* o http?://*  a URL
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+)|(http?://[^\s]+))','URL',tweet)
    #Converte @username a AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remuove spazi vuote ripetuti
    tweet = re.sub('[\s]+', ' ', tweet)
    #Sostituisce #parola con parola [forse non lo vogliamo fare veramente]
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet
#end

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end
 
#start getStopWordList
def getStopWordList(stopWordListFileName):
    # leggi il file di stopwords e crea una lista
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')
 
    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords
#end
 
#start getfeatureVector
def getFeatureVector(tweet):
    featureVector = []
    #separa il tweet per praole
    words = tweet.split()
    for w in words:
        #sostituisci ripetizioni
        w = replaceTwoOrMore(w)
        #rimuovi punteggiatura [forse non lo vogliamo, perchè può rimuovere gli emoticon]
        #w = w.strip('\'"?,.')
        #controlla ce la parola inizi per una lettera
        #val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        val = w
        #ignora le stopwords
        if( w in stopWords or val is None ):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector
#end

#start extract_features
def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features
#end

#Legge i tweet uno per uno e li processa
fp = open('twitts.csv', 'r', encoding="utf8")
inpTweets = csv.reader(fp, delimiter=',', quotechar='"')
stopWords = getStopWordList('feature_list/stopwords.txt')
out1 = codecs.open('out1.txt', 'w', encoding='utf-8')
out2 = codecs.open('out2.txt', 'w', encoding='utf-8')
out3 = codecs.open('out3.txt', 'w', encoding='utf-8')
tweets = []
featureList = []
for line in inpTweets:
    sentimentVector = ( line[1], line[2], line[3], line[4], line[5] )
    processedTweet = processTweet(line[6])
    featureVector = getFeatureVector(processedTweet)
    featureList.extend(featureVector)
    tweets.append((featureVector, sentimentVector));
    #print(sentimentVector)

    #processedTweet
    out1.write('"')
    out1.write(processedTweet)
    out1.write("\n")

    #featureVector
    out2.write('"')
    for a in featureVector:
        out2.write(a)
        out2.write(" ")   
    out2.write('"\n')

# Remove featureList duplicates
featureList = list(set(featureList))
print(len(featureList))
print(featureList[0], featureList[1])

#featureVector
out3.write('"')
for a in featureList:
    out3.write(a)
    out3.write(", ")   
out3.write('"\n')


#st = open('feature_list/stopwords.txt', 'r')
# stopWords = getStopWordList('feature_list/stopwords.txt')
# out1 = codecs.open('out1.txt', 'w', encoding='utf-8')
# out2 = codecs.open('out2.txt', 'w', encoding='utf-8')
# #out3 = codecs.open('out3.txt', 'w', encoding='utf-8')
# line = fp.readline()
# while line:
#     processedTweet = processTweet(line)
#     featureVector = getFeatureVector(processedTweet)

#     #processedTweet
#     out1.write('"')
#     out1.write(processedTweet)
#     out1.write("\n")

#     #featureVector
#     out2.write('"')
#     for a in featureVector:
#         out2.write(a)
#         out2.write(" ")    
#     out2.write('"\n')
    
#     line = fp.readline()
#end loop

fp.close()
#st.close()
out1.close()
out2.close()