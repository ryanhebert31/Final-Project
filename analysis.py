#Name: Ryan & Emily 
#Final Program/Analysis: Mini Search Engine with Analysis
#Description: Parser class separates training data 
#             Cleans training data and creates an inverted index
#             Gets query file and parse queries into dictionary, cleans query when necessary
#             Calculates cosine similarity using calculated weights from query and inverted index
#             Creates dictionary with top 5 most relevant documents for each query
#             Compare program results with most relevant docs for each query given in cranqrel
#             Calculates precision and recall 
#Note: Our paper with precision/recall data is in the ReadMe file
#Known Bugs: None

    
#imports
import re, requests, os, json, math
from nltk.stem import PorterStemmer 
from newspaper import Article
from Parser import Parser


### Main
def main():
    #menu
    print("Welcome to the search engine.")
    #inverted index
    createIndex(r"separated")
    print("Data has been loaded and inverted index created.")
    
    q = getQuery()
    cosineSim(q)
    analysis()


#global variables
STOP_WORDS = False
STEMMING = False
ANALYSIS = {}


###Inverted Index

#get rid of stop words
def cleanSW(words):
    sw = []
    swords = open("sw.txt", 'r')
    swords = swords.read()
    for word in swords.split():
        word =  word.strip()
        sw.append(word)
    out = [word for word in words.split() if not word.lower() in sw]
    output = " ".join(out)
    return output

#clean punctuation    
def cleanPunct(words):
    words = re.sub(r'[^\x00-\x7f]',r'', words) # removes garbage chars 
    return re.sub(r'[^\w\s]', '', words) # removes punctuation 

#clean numbers
def cleanNums(words):
    return re.sub(r'\d+', 'num', words)

#create inverted index
def createIndex(direct):
    global STEMMING
    global STOP_WORDS

    ivIndex = {}
    greatest = 0
    for f in os.listdir(direct):
        #get file number 
        if f.startswith("cranfield"):
            x = re.compile(r'cranfield(\d+).txt')
            srch = x.search(f)
            fileNum = srch.group(1)
            fileNum = int(fileNum)
            if fileNum > greatest:
                greatest = fileNum
            #read contents
            content = open(os.path.join(direct, f), 'r', encoding = 'latin-1')
            contentStr = content.read()
            #clean text
            contentStr = cleanPunct(contentStr.strip())
            contentStr = cleanNums(contentStr)
            
            #remove stop words
            if STOP_WORDS:
                contentStr = cleanSW(contentStr)

            first = True
            for word in contentStr.split():
                #ignore url at top of file 
                if first:
                    first = False
                    continue
                #stem words
                if STEMMING:
                    stemmer = PorterStemmer()
                    word = stemmer.stem(word)
                    
                word = word.lower()
                #check for word
                iv = ivIndex.get(word, -99)
                #if found
                if iv != -99:
                    #update index 
                   iv[fileNum] = iv.get(fileNum, 0) + 1
                   ivIndex[word] = iv
                #add word, file num and count to index
                else:
                    ivIndex[word] = {fileNum : 1}

    #hold greatest file number
    ivIndex["SettingsSettings"] = {"LARGEST_WORD" : greatest}
    #create json file
    with open("invertedIndex.json", 'w') as fb:
         json.dump(ivIndex, fb, indent = 4)

###Retrieval

#get queries and clean them
def getQuery():
    #get query file and parse queries into dictionary
    query = Parser("cran.qry")
    queriesDict = query.parseQueries()
    #for every query
    for key,value in queriesDict.items():
        #remove stop words 
        if STOP_WORDS:
             queriesDict[key] = cleanSW(value)
        #stem words 
        if STEMMING:
             q = ""
             stemmer = PorterStemmer()
             for word in value:
                 q = q + stemmer.stem(word) 
                 queriesDict[key] = q  
    return queriesDict
    
#create query dictionary
def queryIndex(q):
    qDict = {}
    for word in q.split():
        qDict[word] = qDict.get(word, 0) + 1
    return qDict


#caclulate TFIDF and cosine similarity of each doc containing word from query
def cosineSim(q):
    global ANALYSIS
    counter = 0
    #open and load inverted index
    with open("invertedIndex.json", 'r') as iv:
        invertedIndex = json.load(iv)
    #for every query
    for key,value in q.items():
        counter += 1
        #get greatest file num to create range for list of lists 
        LARGEST_WORD = invertedIndex["SettingsSettings"]["LARGEST_WORD"]
        sumW = [0 for x in range(1, LARGEST_WORD + 2)]
        sumQuery = [0 for x in range(1, LARGEST_WORD + 2)]
        sumDoc = [0 for x in range(1, LARGEST_WORD + 2)]
        sumTotal = [(0,0) for x in range(1, LARGEST_WORD + 2)]
    
        #calculate tf for query 
        qDict = queryIndex(value)
        for word in value.split():
            tf = qDict[word]/max(qDict.values())
            idf = math.log(LARGEST_WORD/len(invertedIndex.get(word,[1])))
            Wiq = tf * idf
    
            #calculate tf and idf for query word in inverted index
            for i in range(1, LARGEST_WORD + 1):
                tfDoc = 0
                idfDoc = 0
                x = invertedIndex.get(word, 0)
                if x != 0:
                    y = x.get(str(i), 0)
                    if y != 0:
                        tfDoc = y/LARGEST_WORD
                        idfDoc = math.log(LARGEST_WORD/len(invertedIndex.get(word)))
                #calculate weight of word
                Wij = tfDoc * idfDoc
                #calculate sum of weights
                sumW[i] = sumW[i] + (Wij * Wiq)
                #calculate sum query weights squared
                sumQuery[i] = sumQuery[i] + (Wiq ** 2)
                #calculate sum doc weights squared
                sumDoc[i] = sumDoc[i] + (Wij ** 2)
        
        #calculate cosime similarity
        for i in range(1, LARGEST_WORD + 1):
            sumTotal[i] = (i, sumW[i] / (math.sqrt(sumQuery[i]) * math.sqrt(sumDoc[i]) + 1.0))
        
        #sort results
        sumTotal = sorted(sumTotal, reverse = True, key=lambda tup: tup[1])
        #get doc number of top 5 results
        bestFive = []
        for x in sumTotal:
            bestFive.append(x[0])
        bestFive = bestFive[:5]
        #append list to analysis dictionary with query num as key
        ANALYSIS[counter] = bestFive
   
#calculate percision and recall
def analysis():
    global ANALYSIS
    truePos = 0
    falsePos = 0
    falseNeg = 0
    #get cranqrel data and parse into dictionary
    train = Parser("cranqrel")
    tDict = train.parseTraining()
    #for every query and its list of relevant docs
    for query,docs in ANALYSIS.items():
        #for every relevant doc in list
        for guessRel in docs:
            #get list of relevant docs from train data
            try:
                trainRelList = tDict[str(query)]
            except:
                continue
            #for every relevant doc in list
            for trainRel in trainRelList:
                #program says its relevant and it is relevant
                if guessRel == int(trainRel[0]) and int(trainRel[1]) > 0 and int(trainRel[1]) < 4:
                    truePos += 1  
                #program says not relevant but it is relevant
                elif guessRel != int(trainRel[0]) and int(trainRel[1]) > 0 and int(trainRel[1]) < 4:
                    falseNeg += 1
                #program says its relevant but it is not relevant
                else:
                    falsePos += 1

    #calculate values and print
    percision = truePos/(truePos + falsePos)
    recall = truePos/(truePos + falseNeg)
    print("Percision: " + str(percision))
    print("Recall: " + str(recall))
                

main()