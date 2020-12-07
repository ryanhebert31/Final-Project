# AI Final Program: Emily & Ryan

This program implements a web crawler, scraper, and cosine similarity algorithm to act as a search
engine for the domain https://www.muhlenberg.edu/.

## Installation & Usage

There are no command line arguments necessary to run this program. Simply run the following in a shell/kernel: 
```bash
python final.py
```
or
```bash
python3 final.py
```
if using Python 3. 

## Known Bugs
- We have infrequently run into maximum recurse limits, depending on the machine running and memory available. 

## Development Steps

### Web Crawler
Starting at https://www.muhlenberg.edu/, our crawler method pulls the HTML from the current site and evaluates each link found. All links are added to a stack (list of string), and the HTML contents are written to a file, along with the plain text written to another. These files are found in the files subdirectory. 

At each recurse, we pop off the stack and evaluate the base case condition: have we hit our maximum page depth or is the stack empty? If so, the base case is satisfied and all recurses are popped off the stack. If not, we evaluate the current link to ensure it is within the domain. The process is then repeated. 

The following snippet shows how we retrieve the HTML and a list of urls found: 

```python 
import re, requests

data = requests.get(current).text
urls = re.findall(r'href=[\'"]?([^\'" >]+)', data)
```

There was no trouble at this step as a majority of the code was recycled from the previous homework. 

### Inverted Index
To create our invertex index, we first enter all text files of the subdirectoy and read word for word its contents, disregarding the leading URL. The contents are cleaned of numbers, punctuation, stopwords and stemmed. Our index is a dictionary with the format key: string, value: dictionary, where the subdictionary has the format key: int, value: int. The outer layer dictionary key is each unique word found in all files. The inner dictionary list key represents the file number and value represents the count of that word in that file. 

In the following example, the word "house" is in file 1 twice and file 4 thrice.

```json
{
    "house" : {
        "1": 2,
        "4": 3
    }
}
```

The following snippet shows how we created our inverted index:

```python
ivIndex = {}
for word in currentFile:
    iv - ivIndex.get(word, -99)
    if iv != -99:
        iv[fileNum] = iv.get(fileNum, 0) + 1
        ivIndex[word] = iv
    else:
        ivIndex[word] = {fileNum: 1}
```

The following snippet shows how we wrote the formatted inverted index to a json file:

```python
with open("invertedIndex.json", 'w') as fb:
    json.dump(ivIndex, fb, indent = 4)
```

In order to save time, we added an entry to the ivIndex whose key is SettingsSettings, in which we could store metadata about our inverted intex. We did this mainly to store the largest file number we parse to use as the maximum for the next steps calculations. 

The hardest part of this step was that we constantly forgot the format we were using for our index. We lost track of which number represented what, and what variable stored what dictionary. 


### Retrieval 
To run our calculations, we first calculated the term frequency and inverse document frequency. This was done for each word of the query, run against each word of the inverted index. In other words, we looked word by word in the query and searched for matching words in the inverted index to ensure no wasted time looking at documents not containing a word from our query. We chose to skip calcualtions of the inverse document frequency for the query, since it will always be 1 for a single query. 

Below you see the retrieval of a setting as discussed previously, as well as four lists we used to hold calculations:

```python
LARGEST_WORD = invertedIndex["SettingsSettings"]["LARGEST_WORD"]
sumW = [0 for x in range(1, LARGEST_WORD + 2)]
sumQuery = [0 for x in range(1, LARGEST_WORD + 2)]
sumDoc = [0 for x in range(1, LARGEST_WORD + 2)]
sumTotal = [(0,0) for x in range(1, LARGEST_WORD + 2)]
```

We ran into trouble with list indexes, which is why we initialize these lists from 1 to 1 greater than LARGEST_WORD. Although this results in an extra entry in the list, it was the only way to get rid of an error and we handle the extra 0 later in the code. 

The following loop calculates the tf-idf for a single word of the query: 

```python
for i in range(1, LARGEST_WORD + 1):
    tfDoc = 0
    idfDoc = 0
    x = invertedIndex.get(word, 0) # outer dictionary 
    if x != 0:
        y = x.get(str(i), 0) # inner dictionary 
        if y != 0:
            tfDoc = y/LARGEST_WORD
            idfDoc = math.log(LARGEST_WORD/len(invertedIndex.get(word)))
    # calculate weight of word
    Wij = tfDoc * idfDoc
    # calculate sum of weights
    sumW[i] = sumW[i] + (Wij * Wiq)
    # calculate sum query weights squared
    sumQuery[i] = sumQuery[i] + (Wiq ** 2)
    # calculate sum doc weights squared
    sumDoc[i] = sumDoc[i] + (Wij ** 2)
```

After this loop, each list will have a calculation at the index correlating to the document number. To calculate the cosine similarity, we used the following loop, which outputs a tuple of document number and cosine similarity.

```python
for i in range(1, LARGEST_WORD + 1):
    sumTotal[i] = (i, sumW[i] / (math.sqrt(sumQuery[i]) * math.sqrt(sumDoc[i]) + 1.0))
```

We then sorted sumTotal with the native python sort method. In the end, we had a list of tuples whose first index is the document number, where the first element reflected the document most related to the query, and the last document least related. 

Our hardest part of implementation was figuring out the lists to maintain access to the document numbers. Calculating the variables was simple, but we needed to preserve the document numbers to later retrieve the URLs. 

In order to extract just the plain text, we used the Newspaper3k library. 

### Display
In order to display our results like a search engine would, we implemented a pagination alrogithm. Receiving the list of results, we showed increments of 10 results up until a cosine similarity of 0.0 was shown. To display, we printed the document number, similarity score and URL associated with that document. There were no problems associated with this section as it was simple I/O and printing. No special data structures or libraries were needed. 

### GUI
We opted against implementing a GUI. While possible to complete, we decided python GUIs built with the time we had remaining often looked poor and likely wouldn't result in many points added. 

### Parser
We created a class for parsing the queries, documents and their relations. This can be found in Parser.py. We used regular expressions to parse the data we needed for each. One parser object should correlate to one action, which can then be called as a method. For example, to parse the queries:

```python
queryParser = Parser("cranquery")
queryParser.parseQueries()
```

in which the parameter is the file to parse. 

### Analysis
Stopwords & Stemming ON:
Precision = 0.05
Recall = 0.02

Stopwords ON & Stemming OFF:
Precision = 0.11
Recall = 0.03

Stopwords OFF & Stemming ON:
Precision = 0.05
Recall = 0.01

Stopwords & Stemming OFF:
Precision = 0.11
Recall = 0.03

Without getting into which settings configuration worked best, we noticed that our search engine is not that accurate regardless. Our best results came from both stopword removal and no stemming, which was marginally better than both these settigns defaulted as off. This is somewhat confusing but we can conclude that, in this case, stemming has hurt our performance based on these metrics. Stemming can potentially confuse words with similar beginnings, making our model match more tokens as related when they are actually not. Stop words seemed to have helped our accuracy by giving more weight to more relavent words by removing the unnecessary common words like "and", "but" or "the". These results were definitely not as high as we expected, but we've checked our math and even self-supervised a few calculations and found that our precision and recall is higher when we inspect the document-query relationship than it is when we do so programatically. For example, we found query 1 to be highly related to document 172, though this doesn't show in our model because 172 is not a part of the cranqrel relationship document. 

## License
N/A
