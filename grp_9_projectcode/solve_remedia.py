'''
    Author:
        Santosh
        Rajesh
'''
import os
import os.path
import sys
import re
import nltk
from nltk import sent_tokenize,word_tokenize,pos_tag
import subprocess
from PyDictionary import PyDictionary
import tense_kparser
import traceback
from datetime import datetime

exceptString=["/","'"]
numQuestions=5
where = "Where"
who = "Who"
when = "When"
why = "Why"
what = "What"

idToQueMap={"1":who, "2":what, "3":when, "4":where, "5":why}
iterateQ=[who,what,when,where,why]


aspIOLocation = "./aspIO/"
aspLocation = "../aspAPI/"
rootLocation = "./NLP-REMEDIA/all-remedia-4/"
resultsFilePath = "resultsFile.txt"
aspArguments =""
level = ""
inputFileName = ""
outputFileName = ""
ne_location = ""
main_location = ""
coref_location = ""
answer_location = ""

def buildFileNames(levelNo, fileNumber):
        global aspArguments
        global level
        global inputFileName
        global outputFileName
        global ne_location
        global main_location
        global coref_location
        global answer_location
        levelNo = str(levelNo)
        fileNumber = str(fileNumber)
        aspArguments = levelNo+fileNumber
        level = "level"+levelNo
        inputFileName = aspIOLocation+"aspInput"+aspArguments+".txt"
        outputFileName = aspIOLocation+"aspOutput"+aspArguments+".txt" 
        ne_location = rootLocation+level+"/ne/rm"+levelNo+"-"+fileNumber+".txt.ne"
        main_location = rootLocation+level+"/org/rm"+levelNo+"-"+fileNumber+".txt"
        coref_location = rootLocation+level+"/coref/rm"+levelNo+"-"+fileNumber+".txt.coref"
        answer_location = rootLocation+level+"/snra/rm"+levelNo+"-"+fileNumber+".txt.snra"


class Sentence():
    def __init__(self,sentId,value):
        self.sentId = sentId
        self.sentValue = value
        self.corefValue = ""
        self.question = False
        self.neMap = {}
        self.nnp = []
        self.vb= []
        self.nn = []
        self.vbSynList = []
        self.nnSynList = []
        self.mainVerbTenseList=[]
        self.whereCount = 0
        self.aspMap = '' #object
        self.answerSentId = []
        self.qType= "" # where,when,why,..
 
 
def commonFileRules(data):

    '''
       REMOVE EXCEPTIONS WHILE READING FILES (COREF and NE)
    '''
    data = data[47:]
    # data=data.replace('.',' .')
    #data=data.replace('.</','. </')#only for coref
    data=data.replace('.</','. </')#only for coref
    data=data.replace('Mr. ','Mr ')# TODO
    data=data.replace('Mrs. ','Mrs ')# TODO
    data=data.replace('Dr. ','Dr ')# TODO
    data=data.replace('U.S.A.','USA')# TODO
    data=data.replace('."','.')# TODO
    data=data.replace('.,',',')# TODO
    data=data.replace('Conn.','Conn')# TODO
    data=data.replace('Oct.','Oct')# TODO
    data=data.replace('ST.','ST')# TODO
    data=data.replace('D.C','DC')# TODO
    data=data.replace('DC.','DC')# TODO
    data=data.replace('\xe2','') # TODO, 3 30 Columbus'
    data=data.replace('\xef\xbf\xbd','') # TODO, 3 30 Columbus'

    for i in range(numQuestions):
        t=re.findall('.*?('+str(i+1)+'.*?\..*?Wh).*?\?',data)[0]
        data=data.replace(t,t.replace('.','#'))
    return data
 
class Paragraph():        
 
    def __init__(self,correctIn,totalRead,id, inputMainFile,inputNeFile,inputCorefFile,inputAnswerFile):
        self.paragraphId = id
        self.inputNeFile=inputNeFile
        self.inputMainFile=inputMainFile
        self.inputCorefFile=inputCorefFile
        self.inputAnswerFile = inputAnswerFile
        self.paragraph = ""
        self.sentMap = {} # id vs sent obj
        self.sentenceList = []
        self.questionMap = {}
        self.questionToAnswer={}
        self.correctness = 0
        self.emptiness = 0
        self.correctInOne=0
        self.correctInTwo=0
        self.correctInThree=0
        self.totalRead = totalRead

        self.correctIn = correctIn

        self.run()
 
    def run(self):
        self.paragraph = commonFileRules(open(self.inputMainFile,'r').read())
        self.rules()
        self.sentenceList = sent_tokenize(self.paragraph)
        #print  "7777777"
        #print len(self.sentenceList)
        for sentId in range(len(self.sentenceList)):
            sentObj = Sentence(sentId,self.sentenceList[sentId])
            self.sentMap[sentId] = sentObj
            print sentId, self.sentenceList[sentId]
         
        # returns ne map  for a sentence. map contains 3 keys: LOCATION, TIME, PERSON. and values.
        # return null if the sentence doesnt have any of the fileNumber
        neModule(self)
 
        # replaces the coref of each sentence and stores  this new corefered sentence for each sentence obj
        CorefModule(self)
         
        # get asp graph for each sentence and stores this as a map of map of list
        self.getAspMaps()
 
        # get all the questions from the paragraph
        self.extractQuestions()
        # print "printing the question map"
        # for i in self.questionMap:
        #     print i,self.questionMap[i][0].corefValue
 
        answerModule(self)

        # compares hasMap for each sentence in the paragraph to the question given. and returns count
        self.getAnswers()
        print "-------------------"
        print "Done with Paragraph: "+self.paragraphId+" CORRECTNESS COUNT: " + str(self.correctness)
        print "-------------------"


    def getAspMaps(self):
        
        s = ""
        for sent in self.sentMap:
            obj=self.sentMap[sent]
            s+=obj.corefValue+"@@@@"
        asp=getHasData(s).split("@@@@")
        i=0
        #print len(self.sentMap)
        for id in self.sentMap:
            obj=self.sentMap[id]
            obj.aspMap=ConstructMap(asp[id])
            #print id, obj.corefValue
            i+=1
        #print "------------------------------------------------------"


    def getAnswers(self):
        """
        """
        qcount=0
        for qType in iterateQ:
            qcount+=1
            anyQuestion = self.questionMap[qType]
            
            
            if len(anyQuestion[0].answerSentId)!=0:
                if qType not in self.totalRead:
                    self.totalRead[qType] = 0
                self.totalRead[qType] += 1


            ansCountMap={}
            q=""
            print "------------COMPARING EACH QUESTION WITH EVERY SENTENCE OF THE PARAGRAPH------------\n"

            for w in anyQuestion:
                q1 = w.corefValue
                print "---------COMPARING WITH QUESTION TYPE: "+qType+"------------"
                print q1
                q=q1
                
                for id in self.sentMap:
                    p1= self.sentMap[id].corefValue
                    print "-----COMPARING TO SENTENCE, QUESTION TYPE: "+qType+"----"
                    print p1
                    

                    c=CompareAspMaps(w,self.sentMap[id]).count

                    li=[]
                    if c in ansCountMap:
                        li = ansCountMap[c]
                    li.append(id)
                    ansCountMap[c]= li

            print "======================================================================="
            print "======================================================================="
            print "############QUESTION TYPE: "+qType+"############"
            print q
            print "1st three answers:"
            gotCorrectAns=False
            firstThreeAns=0
            print ansCountMap
            for i in sorted(ansCountMap.keys(),reverse=True):
                


                for id in ansCountMap[i]:
                    firstThreeAns+=1    
                    if gotCorrectAns==True:
                        break
                    

                    if id in anyQuestion[0].answerSentId:
                        if firstThreeAns<=3:
                            self.correctness+=1

                            if firstThreeAns not in self.correctIn:
                                self.correctIn[firstThreeAns] = {}

                            if qType not in self.correctIn[firstThreeAns]:
                                self.correctIn[firstThreeAns][qType]=0    
                            self.correctIn[firstThreeAns][qType]+=1


                            if(firstThreeAns==1):
                                self.correctInOne+=1
                            if(firstThreeAns==2):
                                self.correctInTwo+=1
                            if(firstThreeAns==3):
                                self.correctInThree+=1
                        gotCorrectAns=True
                        
                        # if firstThreeAns<3:
                        #     self.correctness+=1self.paragraphId
                    print "---------------Paragraph  : "+str(self.paragraphId)+"-----Checking in: "+str(firstThreeAns)+"----------"
                    print "ID           : "+ str(id)
                    print "EXACT ANS ID : "+ str(anyQuestion[0].answerSentId)
                    print "FOUND ANSWER : "+ self.sentMap[id].corefValue
                    for t in anyQuestion[0].answerSentId:
                        print "EXACT ANSWER : "+self.sentMap[t].corefValue

                     
                    print "MATCH COUNT  : "+ str(i)
                    print "---------------"
                    print "-------till now correct in first three--------"+ str(self.correctness)+"/"+str(qcount)+"\n"
                    if len(anyQuestion[0].answerSentId)==0:
                        break
                if len(anyQuestion[0].answerSentId)==0:
                    print "Answer not tagged in corpus or Coref file not available for this paragraph. Skip this question"
                    self.emptiness+=1
                    break
                

    def extractQuestions(self):
        """
        """
        for id in reversed(self.sentMap.keys()):
            delete=False
            # if self.sentMap[id].sentValue[2] != "#":
            if "#" not in self.sentMap[id].sentValue:
                break
            self.sentMap[id].question=True
            self.sentMap[id].mainVerbTenseList = tense_kparser.determine_tense_input(self.sentMap[id].corefValue)
            
            if where in self.sentMap[id].sentValue:
                if where not in self.questionMap:
                    self.questionMap[where]=[]
                self.questionMap[where].append(self.sentMap[id])
                self.questionMap[where][0].qType=where
                delete=True
            elif when in self.sentMap[id].sentValue:
                if when not in self.questionMap:
                    self.questionMap[when]=[]
                self.questionMap[when].append(self.sentMap[id])
                self.questionMap[when][0].qType=when
                delete=True
            elif who in self.sentMap[id].sentValue:
                if who not in self.questionMap:
                    self.questionMap[who]=[]
                self.questionMap[who].append(self.sentMap[id])
                self.questionMap[who][0].qType=who
                delete=True
            elif why in self.sentMap[id].sentValue:
                if who not in self.questionMap:
                    self.questionMap[why]=[]
                self.questionMap[why].append(self.sentMap[id])
                self.questionMap[why][0].qType=why
                delete=True
            elif what in self.sentMap[id].sentValue:
                if what not in self.questionMap:
                    self.questionMap[what]=[]
                self.questionMap[what].append(self.sentMap[id])
                self.questionMap[what][0].qType=what
                delete=True
            
                
            #print "----------------123-----------------"
            #print self.sentMap[id].corefValue
            #print self.sentMap[id].mainVerbTenseList
            #print "----------------123-----------------"
 
            if delete:
                self.sentMap.pop(id, None)
    def rules(self):
        """
        """
 
    def printSentMap(self):
        print "##############"
        for key in self.sentMap:
            print ">>>>>>>>>>>>>>>>>>>>"
            print key
            print self.sentMap[key].sentValue
            print self.sentMap[key].corefValue
            print self.sentMap[key].neMap
            print ">>>>>>>>>>>>>>>>>>>>"
        print "##############"
 
 
def getWordlist(sent):
 
    text = word_tokenize(sent.corefValue)
    rmap = {}
    nnplist = []
    nnlist = []
    vblist = []
    nnSynl = []
    vbSynl = []
    lis = nltk.pos_tag(text)
    for i in lis:
        if i[1] in ["NNPS" ,"NNP"]:
            nnplist.append(i[0])
        elif i[1] in ["NN" ,"NNS"]:
            nnlist.append(i[0])
            nnSynl.append(getSyn(i[0]))
        elif i[1] in ["VBZ" , "VBP" , "VBG" , "VBD" , "VBN" ,"VB" , "MD"]:
            vblist.append(i[0])
            vbSynl.append(getSyn(i[0]))
            #print i[0]
 
    sent.nnp = nnplist
    sent.nn = nnlist
    sent.vb = vblist
    sent.nnSynList = nnSynl
    sent.vbSynList = vbSynl
 
def getSyn(word):
    dic = PyDictionary() 
    syn = dic.synonym(word)
    return syn
    #return [k.encode('UTF8') for k in syn]
 
 
 
def getMatchGivenTwoLists(ques_list, sent_list):
    count = 0
    for i in ques_list:
        if i in sent_list:
            count = count+1
    return count
 
def returnCountDoSemanticCompare(qlist, slist, qType):
    
    semanticWhen = ['time','number']
    semanticWhere = ['location']
    semanticWho = ['person']

    count =0
    if qType == when:
        for j in slist:
            if j in semanticWhen:
                print "SEMANTICS for 'WHEN' FOUND, INCREASE BY 10 :"+ j+"=="+j + "---MatchCount: "+ str(count)
                count+=10
    elif qType == where:
        for j in slist:
            if j in semanticWhere:
                print "SEMANTICS for 'WHERE' FOUND, INCREASE BY 10 :"+ j+"=="+j + "---MatchCount: "+ str(count)
                count+=10
    return count

def returnCountforTwoSentences(ques,sent,qType):
 
    getWordlist(ques)#["stop","riders","rest"]
    getWordlist(sent)#["riders","stop","swing station"]
    count=0
    countInc = []
    for i in ques.nnp:
        if i in sent.nnp:
            if sent.nnp not in countInc:
                count = count+2
                countInc.append(sent.nnp)
    for i in ques.nn:
        if i in sent.nn:
            count = count+2
        else:
            count = count + getMatchGivenTwoLists(ques.nnSynList, sent.nnSynList)
    for i in ques.vb:
        if i in sent.vb:
            count = count+2
        else:
            count = count + getMatchGivenTwoLists(ques.vbSynList, sent.vbSynList)
    if "LOCATION" in sent.neMap and qType == where:
        count = count+10
        print "LOCATION TAG FOUND. INCREASE BY 10." + "---MatchCount: "+ str(count)
    elif "TIME" in sent.neMap and qType == when:
        count = count+10      
        print "TIME TAG FOUND. INCREASE BY 10" + "---MatchCount: "+ str(count)
    return count
 
 
class neModule():
    def __init__(self,pObject):
        self.pObject=pObject
        self.run()
 
    def run(self):
        f=commonFileRules(open(self.pObject.inputNeFile,'r').read())
        raw=sent_tokenize(f)
        for i in range(len(raw)):
            entities=re.findall('<ENAMEX.*?="(.*?)">(.*?)</ENAMEX>',raw[i])+re.findall('<TIMEX.*?="(.*?)">(.*?)</TIMEX>',raw[i])
            eMap = {}
            for key,val in entities:
                eMap[key]=val
            self.pObject.sentMap[i].neMap = eMap

'''
    Code by Shranith
    
'''
class answerModule():
    def __init__(self,pObject):
        self.pObject = pObject
        self.run()

    def run(self):
        f=commonFileRules(open(self.pObject.inputAnswerFile,'r').read())
        raw = sent_tokenize(f)
        for i in range(len(raw)):
            entities = re.findall('<ANSQ(.*?)>',raw[i])
            if len(entities) != 0:

                for ent in entities:
                    #print self.pObject.sentMap[i].corefValue
                    #print raw[i]
                    #sentMap[i].answerSentId = idToQueMap[entities[0]]
                    quesObj = self.pObject.questionMap[idToQueMap[ent]][0]
                    #if quesObj.answerSentId==-1:
                    quesObj.answerSentId.append(int(i))
                    #print quesObj.sentId ,quesObj.answerSentId,idToQueMap[ent]



class CorefModule():
    def __init__(self,pObject):
        self.pObject = pObject
        self.run()
 
    def run(self):
        """
        """
        f=commonFileRules(open(self.pObject.inputCorefFile,'r').read())
        raw=sent_tokenize(f)
        #print "COREF RAW LENGTH: " + str(len(raw))
        dataMap={}
        for j in range(len(raw)):
            #print j,raw[j]
            tmp=re.findall('<COREF(.*?)><MARKABLE>(.*?)</MARKABLE></COREF>',raw[j])
            for i in tmp:
                refId=""
                if "ID" in i[0]:
                    refId=re.findall('ID="(.*?)".*',i[0])[0]
                    dataMap[refId]=i[1]

        print "-----------------AFTER RESOLVING COREF-------------------"

        for j in range(len(raw)):
            # if j not in self.pObject.sentMap: # TODO
                # break
            corefSentence = self.pObject.sentMap[j].sentValue;
            #print corefSentence
            pt=[]
            try:
                pt=pos_tag(word_tokenize(corefSentence))
            except:
                print "pos_tag error"
                traceback.print_exc()

            if len(pt)==0:
                continue
            ans=[]
            ans.append(pt[0])
            for i in range(1,len(pt)):
                if pt[i-1][1]==pt[i][1] and pt[i][1] == "NNP":
                    ans[len(ans)-1]=(ans[len(ans)-1][0]+" "+pt[i][0],"NNP")
                else:
                    ans.append(pt[i])
            ptMap={}
            for i in ans:
                ptMap[i[0]]=i[1]
 
            duplicate_pronoun_set=[]
            print "-------SENT ID: "+str(j)
            print corefSentence
            corefNewSentence=""
            l=[]
            tmp=re.findall('<COREF(.*?)><MARKABLE>(.*?)</MARKABLE></COREF>',raw[j])
            alreadyReplacedMap = {}

            for i in tmp:
                ref=""
                if "REF" in i[0]:
                    ref=re.findall('REF="(.*?)".*',i[0])[0]
                    if i[1] in ptMap and ptMap[i[1]]  in ["PRP"]:
                        if ref in dataMap:
                            if dataMap[ref] not in duplicate_pronoun_set:
                                l=corefSentence.split(i[1]+" ")
                                duplicate_pronoun_set.append(dataMap[ref])
                                corefNewSentence=corefNewSentence+l[0]+dataMap[ref]+" "
                                corefSentence=(i[1]+" ").join(l[1:])
                    #corefSentence=corefSentence.replace(i[1],dataMap[ref])
            corefNewSentence= corefNewSentence+corefSentence

            print corefNewSentence 
            self.pObject.sentMap[j].corefValue = corefNewSentence
 

class ConstructMap():
    def __init__(self,data):
        self.data=data
        self.hasMap = {}
        self.hasMapInList = []
        self.run()
    def run(self):
        splitData = self.data.split("\n")
        for line in splitData:
            if line=="":
                continue
            if "has" not in line: # to handle single word sentences
                line="has("+line+")."
            
            (a,b,c)=re.findall(r'has\((.*?),(.*?),(.*?)\).',line)[0]
            
            self.hasMapInList.append(a)
            self.hasMapInList.append(b)
            self.hasMapInList.append(c)
            if '-' in a:
                a=a.split("-")[:-1]
                a='-'.join(a)
 
            c=c.split(',')[0]
            if '-' in c:
                c=c.split("-")[:-1]
                c='-'.join(c)            
            #print a,b,c
            if a not in self.hasMap:
                self.hasMap[a]={}
            if b not in self.hasMap[a]:
                self.hasMap[a][b]=[]
            self.hasMap[a][b].append(c)
        self.hasMapInList = list(set(self.hasMapInList))
    def getmap(self):
        return self.hasMap
    def getmapinlist(self):
        return self.hasMapInList
         
class CompareAspMaps():
    #CompareAspMaps(w.aspMap.getmap(),w.mainVerbTenseList,self.sentMap[id].aspMap.getmap())
    def __init__(self,qObj,sObj):
        self.qObj=qObj
        self.sObj=sObj
        self.qMap=qObj.aspMap.getmap()
        self.sMap=sObj.aspMap.getmap()

        self.qMapInList=qObj.aspMap.getmapinlist()
        self.sMapInList=sObj.aspMap.getmapinlist()

        self.count=0
        self.run()
    def run(self):
        """
        """
        count=0
        flag=0
        print "COMPARING HAS GRAPHS"

        # print self.qObj.corefValue
        # print "----------"
        # print self.qMap
        # print "============="
        # print self.sObj.sentId, self.sObj.corefValue
        # print "----------"
        # print self.sMap
        
        print "-------------------------------------------------"
        print "mainVerbTenseList: "+ str(self.qObj.mainVerbTenseList)
        
        qVerbTenseList=self.qObj.mainVerbTenseList

        for key1 in self.sMap:
            if key1 in self.qMap or key1 in qVerbTenseList:
                if key1 in qVerbTenseList:
                    print key1 + " found in question VerbTenseList" + "---MatchCount: "+ str(count)

                    '''
                    increasing count by 10. Sentence avg length is assumed as 10. And this value will 
                    nullify the effect of other unwantted sentences dominating the current sentence.
                    '''
                    count+=10
                print key1+"=="+key1
                count+=1;
                for key2 in self.sMap[key1]:
                    if key1 in self.qMap:
                        if key2 in self.qMap[key1]:
                            print key2+"=="+key2 + "---MatchCount: "+ str(count)
                            count+=1;
                            l1 = self.qMap[key1][key2]
                            l2 = self.sMap[key1][key2]
                            for e1 in l1:
                                if e1 in l2:
                                    print e1+"=="+e1 + "---MatchCount: "+ str(count)
                                    count+=1;

        print "-------------------------------------------------"
        print "CHECKING FOR SYNONYMS:\n"
        
        count += returnCountforTwoSentences(self.qObj,self.sObj,self.qObj.qType)
        
        print "-------------------------------------------------"
        print "CHECKING FOR SEMANTICS\n"

        count += returnCountDoSemanticCompare(self.qMapInList,self.sMapInList,self.qObj.qType)
        
        print "================================================="
        print "Final Match Count for this Sentence= ",count
        print "=================================================\n"

        self.count= count

 
def getHasData(data):
    if os.path.isfile(outputFileName) == True:
        print "ASP outputFileName present " + outputFileName
        print "Hence not calling KPARSER JAR\n"
        return open(outputFileName,'r').read()
    else:
        print "ASP outputFileName not present " + outputFileName
        print "Hence calling KPARSER JAR\n"
        f=open(inputFileName,'w')
        print inputFileName
        f.write(data)
        f.close()
        p = subprocess.Popen(["java","GenerateAspGraph",aspArguments], cwd=aspLocation)
        p.wait()
        return open(outputFileName,'r').read()
 
def test():
    start = datetime.now()
    resultsFile = open(resultsFilePath,'a+')
    resultsFile.write("$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
    resultsFile.write("$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n")


    resultsFile.close()
    levelNo = [2,3,4,5]
    for level in levelNo:
        correctIn = {}
        totalRead = {}
        correct=0
        totalChecked=0
        avg=0
        correctInOne=0
        correctInTwo=0
        correctInThree=0
        for i in range(1,31):
            buildFileNames(level, i)
            print main_location
            if os.path.isfile(main_location) == True and os.path.isfile(coref_location) == True:
                try:
                    resultsFile = open(resultsFilePath,'a+')
                    p = Paragraph(correctIn,totalRead,(str(level)+""+str(i)),main_location,ne_location,coref_location,answer_location)
                    correct = correct + p.correctness
                    totalChecked+=5-p.emptiness
                    correctInOne+=p.correctInOne
                    correctInTwo+=p.correctInTwo
                    correctInThree+=p.correctInThree
                    print correctIn
                    string11 = str(level)+"_"+str(i)+" : "+str(p.correctness)+"/"+ str(int(5-p.emptiness)) + " : "+str(correctIn)
                    print "---------------------------------------------------\n"
                    print string11
                    resultsFile.write(string11)
                    resultsFile.write('\n')
                    resultsFile.close()
                except:
                    print "exception in paragraph " + str(i)
                    traceback.print_exc()
        avg = correct/totalChecked
        c1 = correctInOne
        c2 = c1 + correctInTwo
        c3 = c2 + correctInThree

        a =  "-------------------------------------------------------\n"
        a += str(level)+"_P : " + str(correct) +"/"+str(totalChecked)
        a += " C1: "+ str(c1)+ " C2: "+ str(c2)+ " C3: "+ str(c3) +"\n"
        a += "Correct   : "+str(correctIn)+"\n"
        a += "Total Read: "+str(totalRead)+"\n"
        a += "-------------------------------------------------------\n\n\n"

        resultsFile = open(resultsFilePath,'a+')
        print a
        resultsFile.write(a)
        resultsFile.write("\n")
        resultsFile.close()

    end = datetime.now()
    print end-start
 
test()
