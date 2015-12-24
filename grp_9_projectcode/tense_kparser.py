'''
    AUTHOR
    SAI KUMAR
'''
from nltk import word_tokenize,pos_tag

def determine_tense_input(sentence):

	print sentence+"tensee"
	verblist=[]
	auxVerbList=["be","am","is","are","was","were","been","have","has","had","do","does","did","can","could","may","might","will","would","shall","should","must","oughtto","be","been","am","is","are","was","were","have","has","had","do","does","did","Shall","Should","Will","Would","May","Might","Can","Could","Must"]
	ver=[]  

	text = word_tokenize(sentence)
	tagged = pos_tag(text)
	tense=""
	if tagged[1][1]=='MD':
	    tense='future'
	    
	elif tagged[1][1]=='VBP' or tagged[1][1]== 'VBZ' or tagged[1][1]== 'VBG':
	    tense='present'

	elif tagged[1][1]=='VBD' or tagged[1][1]=='VBN':
	    tense='past'
	#print tense

	for tag in range(len(tagged)):
	    if tagged[tag][1][0]=='V' or tagged[tag][1][0]=='N':
	        verb=tagged[tag][0]
	        verblist.append(verb)

	f=open('verb.txt').readlines()
	verbtenses={}
	for i in range(len(f)):
	    a=f[i].strip().split(",")
	    for l in a:
	        verbtenses[l]=a

	for eachVerb in verblist:
	    if eachVerb in verbtenses and eachVerb not in auxVerbList:
	        ver.extend(verbtenses[eachVerb])

	ver = [i for i in ver if i!= ""]
	#print list(set(ver))
	return list(set(ver))
    
#determine_tense_input("What did Alex eat on the island?")
