import re
import pickle
import operator
import random

def sliceCorpus(corCorpus): #slice corpus into 80-20 for dev + test
    dev, test = [], []#open('dev', 'w'), open('test', 'w')

    for line in corCorpus:
        if random.SystemRandom().randint(0,100) > 20:
            dev.append(line)
            #dev.write(line+'\n')
        else:
            test.append(line)
            #test.write(line+'\n')
    return(dev, test)

def trainTest(dev, test, tagList): #train the HMM model and then test it

    pairs  = twoFreq(dev, tagList)
    words = wordFreq(dev, tagList)

    return (HMMaccuracy(test, tagList, pairs, words))



def nfoldValidation(corCorpus, tagList, n=10): #checar sintaxe

        totalAccuracy = 0

        for i in range(n):
            sliced = sliceCorpus(corCorpus)
            dev, test = sliced[0], sliced[1]

            print('LEN',len(dev),len(test))

            totalAccuracy += trainTest(dev, test, tagList)

        return (totalAccuracy/n)




def twoFreq(corCorpus, allTags): #measure probabilities of, given a pair [a,b] of POS Tags, an observation of C. Input also the tag list.

    freqTable = {'zero': {}}
    regexTag  = '⛬\w*\s'

    tagSize = len(allTags) #needed for laplacian smoothing

    allPairs = ['zero'] #generate a list with all possible combinations of two tags
    for t in allTags:
        freqTable['zero'][t[:-1]] = 1
        first = t[:-1]     #for second word. TAG1 ---> TAG2
        allPairs.append(first)
        for l in allTags:
            allPairs.append(t[:-1]+l[:-1])

    for pair in allPairs:                   #create entry for a particular pair
        freqTable[pair] = dict()
        for tag in allTags:
            freqTable[pair][tag[:-1]] = 1

    for line in corCorpus:
        sentenceTags = re.findall(regexTag, line) #ordered list containing POSTAGS.

        for t in range(len(sentenceTags)):
            tag  = sentenceTags[t][:-1]
            if t == 0:                       #first tag
                if tag in freqTable['zero']:
                    freqTable['zero'][tag] += 1
            elif t == 1:                     #second tag
                if tag in freqTable[sentenceTags[0][:-1]]:
                    freqTable[sentenceTags[0][:-1]][tag] += 1
            else:
                dualTag = sentenceTags[t-2][:-1]+sentenceTags[t-1][:-1]
                freqTable[dualTag][tag] += 1


    ##Convert to probabilities
    for pair in allPairs:#freqTable:

        total = 0

        for tag in freqTable[pair]:
            #print('PAR: ',pair,'TAG: ', tag[:-1])
            total += freqTable[pair][tag]
        for tag in freqTable[pair]:
            freqTable[pair][tag] = freqTable[pair][tag] / total

    #for tag in allTags:
    #    print(freqTable)
    #    print(freqTable[tag[:-1]])
    return (freqTable)

def untagSentence(sentence):  #input is a tagged sentence. Returns a 2-ple of strings, the sentence itself and the tags.
    result, tags, splitSentence = '', [], sentence.split()
    for word in splitSentence:
        if word[0] != '⛬':
            result += word+' '
        else:
            tags.append(word)
    return(result, tags)

def wordFreq(corCorpus, tagList): #generates a dictionary with P(word|tag) statistics

    #pickleName = input('Nome do arquivo Pickle: ')
    tagtoWord = dict()
    for tag in tagList:
        tagtoWord[tag[:-1]] = {}

    regex_tagword = '[^⛬]+\s⛬[A-Z]+'
    #regex_tagword = '\w*[,".:\%$´\\\\ |\'±=\`\&-;!?()\[\]]*\s⛬[A-Z]+'  ###Tive que por a pontuacao na mao! talvez tenha mais. CHECAR!

    for sentence in corCorpus: #split sentence into strings with word+tag
        tagwords = re.findall(regex_tagword, sentence)
        #print(tagwords)

        for t in tagwords: #split string with word+tag into list [word, tag]
            #print(sentence)
            #print(t.split())
            if len(t.split()) == 2:
                word, tag = t.split()[0], t.split()[1]


                if tag in tagtoWord: ### so para testes. Depois tirar quando relimpar o corpus.
                    if word in tagtoWord[tag]:
                        tagtoWord[tag][word] += 1
                    else:
                        tagtoWord[tag][word]  = 1

    #print(tagtoWord)

    # Convert to probabilities

    for tag in tagList:
        total = 0
        for word in tagtoWord[tag[:-1]]:
            total += tagtoWord[tag[:-1]][word]

        for word in tagtoWord[tag[:-1]]:
            tagtoWord[tag[:-1]][word] = tagtoWord[tag[:-1]][word]/total

    #print (tagtoWord)
    #pickle.dump(tagtoWord,open(pickleName, 'wb'))
    return (tagtoWord)

def tagSentence(splitSentence, tagList):
    result = ''
    if len(splitSentence) == len(tagList):
        for i in range(len(splitSentence)):
            result += splitSentence[i]+' '+tagList[i]+' '
    else:
        print('erro')

    return result



def viterbiD(sentence, tagList, twoTagDic, tagWord):

    #ainda está incompleto
    #tags precisam estar corretas - comando tag.strip()

    viterbiScores, backpointersMatrix = [{}], [{}]
    splitSentence = sentence.split()

    #initialization
    viterbiScores[0]['**'] = 1
    backpointersMatrix[0]['*_*'] = 'inicio'

    for k in range(1,len(splitSentence)+1):

        verbiScores.append({})
        backpointersMatrix.append({})

        for tagu in tagList:
            for tagd in tagList:

                allValues = []
                for tagt tagList:
                    allValues.append( [viterbiScores[k-1][tagt+tagu]*twoTagDic[tagt+tagu], tagt] )
                bestScore, bestTag = max(allValues)[0], max(allValues)[1]
                try:
                    viterbiScores[k][tagu+tagd] = bestScore * tagWord[tagd][splitSentence[k-1]]
                except:
                    viterbiScores[k][tagu+tagd] = 0
                backpointersMatrix[k][tagu+'_'+tagd] = bestTag

    #end
    allValues, tagged = [], []
    for tagu in tagList:
        for tagd in Taglist:
            allValues.append([viterbiScores[len(splitSentence+1)][tagu+tagd], backpointersMatrix[len(splitSentence)-1][tagu+tagd] ])
    t = max(allValues)[1]
    for i in range(len(splitSentence),2,-1):
        tagged.append(t)
        t = backpointersMatrix[i][]








def HMMaccuracy(corpus, tagList, twoFreq, wordFreq):
    total, correct = 0,0


    for i in range(len(corpus)):

        #if i%1000 == 0:
        #    print(i)
        s = corpus[i]
        untag, comp = untagSentence(s)[0], untagSentence(s)[1]
        #print(len(untag.split()))
        if len(untag.split())>9:
            #print (len(corpus[i]))


            #untag, comp = untagSentence(s)[0], untagSentence(s)[1]
            vit = viterbi(untag, tagList, twoFreq, wordFreq)
            for t in range(len(comp)):
                total += 1
                try:
                    if vit[t] == comp[t]:
                        correct += 1
                except:
                    print('problema: ', vit, comp, t)
                #else:
                #    print(vit[t],comp[t], untag.split()[t])
    print (correct/total)
    return (correct/total)


'''testes'''

if __name__ == '__main__':
    import pre_proc as pp

    dev        = open('pequenoCorrigido.txt', 'r').readlines()
    tags = open('tags', 'r').readlines()
    #common = pp.likelyTag(dev)
    pairs = twoFreq(dev, tags)
    word  = wordFreq(dev, tags)


    sentence = 'Tem ⛬V sentido ⛬V - ⛬PONT aliás ⛬ADV , ⛬PONT muitíssimo ⛬DET sentido ⛬N . ⛬PONT '
    sent, correctTags = untagSentence(sentence)[0], untagSentence(sentence)[1]
    print(sent)
    print(correctTags)
    viterbiD(sent, tags, pairs, word)
