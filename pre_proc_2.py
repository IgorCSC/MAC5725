import re
import pickle
import operator

#folhona = open('CETENFolha-1.0_jan2014.cg', 'r')
folinha = open('pqeno.cg', 'r')
linesFolinha = folinha.readlines()
#linesFolin = folhona.readlines()

#smallClean = open('pequenoCorrigido.txt', 'r')
#linesSmall = smallClean.readlines()

#cetenClean = open('CETENLimpo.txt', 'r')
#linesClean = cetenClean.readlines()

#arroba = open('CETENarroba.txt', 'r')


def corpusToSentence(corpus):

    corpusName = input('Nome do arquivo do corpus de sentencas: ')
    newCorpus = open(corpusName+'.txt', 'w')

    regexWord = '\w+\s'
    regexTag = '\s[A-Z]+\s'


    for line in corpus:
        if line == '\n': #detecta fim de sentenca
            newCorpus.write('\n')

        elif line[0]=='$':

            word = line[1]
            tag  = 'PONT'

            newCorpus.write(word+' ⛬'+tag+' ')

        elif line[0]!='<':

            word = re.search(regexWord, line)
            tag =  re.search(regexTag,  line)

            try:
                newCorpus.write(word.group()[:-1]+' ⛬'+tag.group()[1:-1]+' ')
                #print(word.group(), tag.group())
            except:
                pass
                #print('No tag: ', line)

    newCorpus.close()

def numTag(corCorpus): #count no of tags
    total = 0
    for line in corCorpus:
        words = line.split()
        for w in words:
            if w[0] == '⛬':
                total += 1
    return total

def counTag(corCorpus):

    noTag = dict() #dictionary w tags as keys and no occurrence as value

    fileName = input('Nome do arquivo para contagem de TAGs: ')
    newFile  = open(fileName+'.txt', 'w')

    for line in corCorpus:
        tags = re.findall('⛬\w*', line)

        #tagsCorrected = [] #take away '[' and ']'
        #for t in tags:
        #    tagsCorrected.append(t[2:-2])

        for t in tags:
            if t in noTag:
                noTag[t] += 1
            else:
                noTag[t] =  1

    for tag in noTag:
        newFile.write(tag)
        newFile.write(' : '+str(noTag[tag]))
        newFile.write('\n')
    newFile.close()

    #print (noTag)

def likelyTag(corCorpus):

    wordDict = dict()
    likelyFile = open(input('Nome do pickle de saida: '), 'wb')

    for line in corCorpus:
        words = line.split()


        #print (words)
        for n in range(0,len(words),2):
            #print (n)
            if n+1 < len(words):
                if words[n] in wordDict:
                    if words[n+1] in wordDict[words[n]]:
                        wordDict[words[n]][words[n+1]] += 1
                    else:
                        wordDict[words[n]][words[n+1]] = 1
                else:
                    wordDict[words[n]] = {words[n+1] : 1}


    print (wordDict)
    for word in wordDict:
        wordDict[word] = max(wordDict[word].items(), key=operator.itemgetter(1))[0]
    print(wordDict)
    pickle.dump(wordDict, likelyFile)


def cutCorpus(corCorpus): #make small file for testing

    newCorpus = open('pequenoCorrigido.txt', 'w')

    for i in range(100):
        newCorpus.write(corCorpus[i])

    newCorpus.close()


def maxTag(sentence, commonDictionary): #pick a sentence. Tag w/ most common tag:

    newSentence = sentence.split()
    taggedSentence = ''

    for word in newSentence:
        try:
            taggedSentence += word+' '+commonDictionary[word]+' '
        except:
            taggedSentence += word+' ⛬DESCONHECIDO '
            print ('deu xabu ', word)
    #print(taggedSentence)
    return(taggedSentence)


def tagAccuracy(corCorpus, commonDictionary): #tag sentences. calc. the percentage of correct tagsself.
    correct, total = 0,0

    for line in corCorpus:
        sentence = ''
        wordlist = line.split()
        for w in wordlist:
            if w[0] != '⛬':
                sentence += w+' '

        tagged = maxTag(sentence, commonDictionary).split()

        for w in range(1,len(wordlist),2):

            if len(wordlist) > len(tagged):
                print (wordlist, tagged)

            total += 1
            if wordlist[w] == tagged[w]:
                correct += 1
            #print (wordlist[w], tagged[w])

    print (correct, total, correct/total)


'''work in progress - ta errado ainda'''
def twoFreq(corCorpus, allTags): #measure probabilities of, given a pair [a,b] of POS Tags, an observation of C. Input also the tag list.

    zero = dict() #not sure if necessary
    freqTable = {'zero': zero}
    regexTag  = '⛬\w*\s'

    for line in corCorpus:
        tagList = re.findall(regexTag, line) #ordered list containing POSTAGS.

        for i in range(len(tagList)):
            if i == 0: #first case
                if tagList[i] in freqTable['zero']:
                    freqTable['zero'][tagList[i]] += 1
                else:
                    freqTable['zero'][tagList[i]] = 1
            elif i == 1: #singleton case
                if tagList[0] in freqTable:
                    if tagList[1] in freqTable[tagList[0]]:
                        freqTable[tagList[0]][tagList[1]] += 1
                    else:
                        freqTable[tagList[0]][tagList[1]] = 1
                else:
                    freqTable[tagList[0]] = {tagList[1]:1}
            else:

                pair = (tagList[i-2],tagList[i-1])

                if pair in freqTable:
                    if tagList[i] in freqTable[pair]:
                        tagList[pair][tagList[i]] += 1
                    else:
                        tagList[pair][tagList[i]] = 1
                else:
                    freqTable[pair] = {tagList[i]:1}

        print(tagList)


'''testes'''
if __name__ == '__main__':

    #corpusToSentence(linesFolinha)

    #arroba = open('CETENarroba.txt', 'r')
    #arroba = open('TESTEARROBA.txt', 'r')
    #miniStar    = open('miniCorpusStar.txt', 'r')
    gigaStar    =open('cetenStar.txt', 'r')

    #counTag(star)
    #likelyTag(gigaStar)

    #wordic = pickle.load(open('starPickle', 'rb'))

    #si = 'PT em o governo'
    #while si != 'quit':
    #    si = input('sentenca: ')
    #    maxTag(si, wordic)

    #tagAccuracy(gigaStar, wordic)
    print(numTag(gigaStar))
