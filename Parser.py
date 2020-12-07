#Name: Ryan & Emily 
#Final Program/Analysis: Mini Search Engine with Analysis
#Description: Parser class to parse given files
#Known Bugs: None

import re, os 

class Parser:
    def __init__(self, path):
        self.filePath = path
        self.queryDict = {}
        self.trainDict = {}
    
    #method to parse cran.qry file
    def parseQueries(self):
        first = True
        #open and ready file
        queryFile = open(self.filePath, "r", encoding = "latin-1")
        
        ID = -1
        for line in queryFile.readlines():
            ## ID?
            #get ID
            if first and line.startswith(".I"):
                first = False
                x = re.compile(r'.I (\d{1,3})')
                idSearch = x.search(line)
                ID = idSearch.group(1)
            #second ID    
            elif line.startswith(".I"):
                x = re.compile(r'.I (\d{1,3})')
                idSearch = x.search(line)
                ID = idSearch.group(1)
                
            ## .W ?? then ignore
            elif line.startswith(".W"):
                continue
            
            ## Query?? 
            #add to query dict with ID as key
            else:
                self.queryDict[ID] = self.queryDict.get(ID, "") + line.strip()
                
        return self.queryDict
        
    #method to parse cranqrel file     
    def parseTraining(self):
        #open and read flile
        trainingFile = open(self.filePath, "r", encoding = "latin-1")
        for line in trainingFile.readlines():
            #regex for format of each line
            x = re.compile(r'(\d{1,3}) (\d{1,3}) (\d)')
            search = x.search(line)
            if search is not None:
                #query num
                doc1 = search.group(1)
                #doc num
                doc2 = search.group(2)
                #relation num
                relation = search.group(3)
                
                #create dictionary with query num as key and list of tuples (doc num, relation) as value
                test = self.trainDict.get(doc1, -1)
                if test == -1:
                    self.trainDict[doc1] = [(doc2, relation)]
                else:
                    self.trainDict[doc1].append((doc2, relation))
          
        return self.trainDict
            
    #method to parse cran.all.1400 into separated files - taken from separateFile.py on Canvas
    def parseData(self):
        Id = 0
        fo = 10
        flag = False
        with open("cran.all.1400") as f:
            for line in f:
                m = re.search(r'(\.I) (\d+)', line)
                if m is not None:          
                    if Id != m.group(2):
                        if int(Id) > 0:
                            fo.close()
                        Id = m.group(2)
                        path = os.path.dirname(os.path.abspath(__file__)) + '/separated'
                
                        filename = "cranfield" +m.group(2)+".txt"
                        filename = os.path.join(path, filename)
                        fo = open(filename, "w")
			    
                        flag = True
                if flag == True:
                    fo.write(line)


                    
        
