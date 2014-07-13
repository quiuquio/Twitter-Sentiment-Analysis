#import regex
import re
import csv
import codecs
import pickle
#import pprint
import random
import nltk.classify

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL) 
    return pattern.sub(r"\1\1", s)
#end

#Split words from punctuation and change emoticons to tokens
def split_special(s):
    smileys =   """
                    :-) :) :o) :] :3 :c) :> =] 8) =) :} :^) 
                    :D 8-D 8D x-D xD X-D XD =-D =D =-3 =3 B^D
                    :-)) :))
                    ;) ;-)
                    :'-) :')
                    ;-) ;) *-) *) ;-] ;] ;D ;^) :-,
                    >:P :-P :P X-P x-p xp XP :-p :p =p :-Þ :Þ :þ :-þ :-b :b d:
                    >:) >;) >:-)
                    *_* 
                    <3 *\0/* \o/ 
                    ^_^ (゜o゜) (^_^)/ (^O^)／ (^o^)／ (^^)/ (≧∇≦)/ (/◕ヮ◕)/ (^o^)丿 ^ω^
                """.split()
    sadys = """ 
                >:[ :-( :(  :-c :c :-<  :っC :< :-[ :[ :{ 
                ;( :-|| :@ >:( :'-( :'( 
                D:< D: D8 D; D= DX v.v D-':
                >:O :-O :O :-o :o 8-0 O_O o-o O_o o_O o_o O-O 
                >:\ >:/ :-/ :-. :/ :\ =/ =\ :L =L :S >.< 
                :| :-| :$ :-X :X :-# :# <:-| ಠ_ಠ  
                </3
            """.split()
    for smiley in smileys:
        s = s.replace(smiley, "positiveemoticon")
    for sad_face in sadys:
        s = s.replace(sad_face, "negativeemoticon")
    s = ''.join(filter(lambda c: c not in '.,!?', list(s)))
    return s
#

#start process_tweet
def processTweet(tweet): 
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',tweet)
    tweet = re.sub('((http?:://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)    
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #split punctuation and emoticons
    tweet =  split_special(tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet
#end 

#start getStopWordList
def getStopWordList(stopWordListFileName):
    #read the stopwords
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
def getFeatureVector(tweet, stopWords):
    featureVector = []  
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences 
        w = replaceTwoOrMore(w) 
        #check for emoticons
        #w = processEmoticons(w)
        #strip punctuation
        w = w.strip('\'"!?,.')
        #check if it consists of only words
        #val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", w)
        val = w
        #ignore if it is a stopWord
        if(w in stopWords or val is None):
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

def getSentimentFromVector(sentVec):
    if sentVec[1] == "1" and sentVec[2] == "1":
        return "mixed"
    elif sentVec[1] == "1":
        return "positive"
    elif sentVec[2] == "1":
        return "negative"
    else:
        return "neutral"

def writeFeatureVector(featureList):
    for a in featureList:
        out3.write(a)
        out3.write(", ")   
    out3.write('"\n')

#Write on processedTweets file
def writeProcessedTweets(processedTweet):
    out1.write('"')
    out1.write(processedTweet)
    out1.write("\n")

#Write on featureVector for each twitt
def writeTwittsFeatures(featureVector):
    out2.write('"')
    for a in featureVector:
        out2.write(a)
        out2.write(" ")   
    out2.write('"\n')

#Write on badly classification file
def writeMisclassfication(classifier, prediction, actual_sentiment, tweet):
    out4.write(prediction)
    out4.write(", ")
    out4.write(actual_sentiment)
    out4.write(", ")
    out4.write(tweet)
    out4.write("\n")

#Read the tweets one by one and process it
def prepareDataFromTweets():
    badCount = 0
    featureList = []
    tweets = []
    for row in inpTweets:
        #sentiment = row[0]
        sentimentVector = ( row[1], row[2], row[3], row[4], row[5] )
        sentiment = getSentimentFromVector(sentimentVector)
        tweet = row[6]

        # We trow away a lot of stuff just to go faster during development
        if random.random() > 0.1:
            continue
        #We discard information about missing data
        if tweet == "Tweet Not Available": 
            badCount = badCount+1
            continue
        #we randomly select part of the data to test and leave the rest for training
        if random.random() > 0.95:
            testTweets.append((tweet, sentiment))
            continue
        processedTweet = processTweet(tweet)
        featureVector = getFeatureVector(processedTweet, stopWords)
        featureList.extend(featureVector)
        tweets.append((featureVector, sentiment));
        #tweets.append((featureVector, sentimentVector)); #we can use the sentiment vector too. It looks like this("1","1","0","0","0","0",)   
        #Write on output files
        writeProcessedTweets(processedTweet)
        writeTwittsFeatures(featureVector)
    # end loop
    print("Twitts processed")
    print("Missing", badCount, "tweets.")
    # Remove featureList duplicates
    featureList = list(set(featureList))
    # Write featureVector on featureVector file
    writeFeatureVector(featureList)
    print("Feature list ready. Length:", len(featureList))
    return (tweets, featureList)

def trainClassifiers(tweets):
    # Generate the training set
    training_set = nltk.classify.util.apply_features(extract_features, tweets)
    print("Training set created!")

    # Train and save the Naive Bayes classifier to a file
    NBClassifier = nltk.NaiveBayesClassifier.train(training_set)
    f = open('data/trained_classifiers/NBClassifier.pickle', 'wb')
    pickle.dump(NBClassifier, f, 1)
    f.close()
    print("NBClassifier Classifier Trained")


    # Train Max Entropy Classifier
    MaxEntClassifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'IIS', trace=2, \
                           encoding=None, labels=None, sparse=True, gaussian_prior_sigma=0, max_iter = 5)
    f = open('data/trained_classifiers/MaxEntClassifier.pickle', 'wb')
    pickle.dump(MaxEntClassifier, f, 1)
    f.close()
    print("MaxEntClassifier Classifier Trained")

    return (training_set, NBClassifier, MaxEntClassifier)

def testClassifiers(testTweets):
    #Test NBClassifier
    results = {"correct": 0, "wrong": 0}
    print("*"*10, "\n")
    print("Now testing", len(testTweets), "tweets with NBClassifier")
    for tw, sent in testTweets:
        processedTestTweet = processTweet(tw)
        sentiment = NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet, stopWords)))
        if sent == sentiment:
            results["correct"] += 1
        else:
            writeMisclassfication("NBClassifier", sentiment, sent, tw)
            results["wrong"] += 1
    print(results)
    total = results["correct"]+results["wrong"]
    acuracy = (results["correct"]/total)*100
    print("Acuracy of", acuracy,"%")
    print(NBClassifier.show_most_informative_features(20))

    #Test NBClassifier
    results = {"correct": 0, "wrong": 0}
    print("*"*10, "\n")
    print("Now testing", len(testTweets), "tweets with MaxEntClassifier")
    for tw, sent in testTweets:
        processedTestTweet = processTweet(tw)
        sentiment = MaxEntClassifier.classify(extract_features(getFeatureVector(processedTestTweet, stopWords)))
        if sent == sentiment:
            results["correct"] += 1
        else:
            writeMisclassfication("MaxEntClassifier", sentiment, sent, tw)
            results["wrong"] += 1
    print(results)
    total = results["correct"]+results["wrong"]
    acuracy = (results["correct"]/total)*100
    print("Acuracy of", acuracy,"%")

    print(MaxEntClassifier.show_most_informative_features(20))

# Test the classifier1
# testTweet = 'Bravo! Hai scritto un classificatore! Che bello!!!! :)'
# processedTestTweet = processTweet(testTweet)
# sentiment = NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet, stopWords)))
# print ("testTweet =", testTweet, "sentiment=", sentiment)

#Globals
inpTweets = csv.reader(open('data/twitts.csv', 'r', encoding="utf8"), delimiter=',', quotechar='"')
stopWords = getStopWordList('data/feature_list/stopwords.txt')
out1 = codecs.open('data/logs/out_processedTweets.txt', 'w', encoding='utf-8')
out2 = codecs.open('data/logs/out_twitts_features.txt', 'w', encoding='utf-8')
out3 = codecs.open('data/logs/out_feature_vector.txt', 'w', encoding='utf-8')
out4 = codecs.open('data/logs/out_badly_classfied.txt', 'w', encoding='utf-8')
count = 0;
featureList = []
tweets = []
testTweets = [] 

# main operations
tweets, featureList = prepareDataFromTweets()
training_set, NBClassifier, MaxEntClassifier = trainClassifiers(tweets)
testClassifiers(testTweets)