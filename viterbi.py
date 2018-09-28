import re
import pickle
import operator
import random
from math import log as log

def twoFreq(corCorpus, allTags):
    '''measure probabilities of, given a pair [a,b] of POS Tags, an observation of C.
    allTags = list of tags
    '''

    freqTable = {'zero': {}}
    regexTag  = '⛬\w*\s'

    tagSize = len(allTags) #needed for laplacian smoothing

    allPairs = [] #generate a list with all possible combinations of two tags
    for t in allTags:
        for l in allTags:
            allPairs.append(t+'_'+l)



    for pair in allPairs:                   #create entry for a particular pair
        freqTable[pair] = dict()
        for tag in allTags:
            freqTable[pair][tag] = 1

    for line in corCorpus:

        sentenceRegex, sentenceTags = re.findall(regexTag, line), [] #ordered list containing POSTAGS.
        for mk in sentenceRegex:
            sentenceTags.append(mk[1:-1])

        for t in range(len(sentenceTags)):
            tag  = sentenceTags[t]
            if t == 0:                       #FIRST TAG
                if tag in freqTable['*_*']:
                    freqTable['*_*'][tag] += 1
            elif t == 1:                     #SECOND TAG
                if tag in freqTable['*_'+sentenceTags[0]]:
                    freqTable['*_'+tag][tag] += 1
            else:                            #OTHER TAGS
                dualTag = sentenceTags[t-2]+'_'+sentenceTags[t-1]
                freqTable[dualTag][tag] += 1

    '''Convert count to probabilities'''
    for pair in allPairs:

        total = 0

        for tag in freqTable[pair]:
            total += freqTable[pair][tag]
        for tag in freqTable[pair]:
            freqTable[pair][tag] = freqTable[pair][tag] / total

    return (freqTable)

def untagSentence(sentence):
    '''input is a tagged sentence. Returns a 2-ple of strings, the sentence itself and the tags.
    '''

    result, tags, splitSentence = '', [], sentence.split()
    for word in splitSentence:
        if word[0] != '⛬':
            result += word+' '
        else:
            tags.append(word)
    return(result, tags)

def wordFreq(corCorpus, tagList):
    '''generates a dictionary with P(word|tag) probabilities
    '''

    tagtoWord = dict()
    for tag in tagList:
        tagtoWord[tag] = {}

    regex_tagword = '[^⛬]+\s⛬[A-Z]+'

    for sentence in corCorpus: #split sentence into strings with word+tag
        tagwords = re.findall(regex_tagword, sentence)

        for t in tagwords: #split string with word+tag into list [word, tag]
            if len(t.split()) == 2:
                word, tag = t.split()[0], t.split()[1][1:]
                if tag in tagtoWord: ### so para testes. Depois tirar quando relimpar o corpus.
                    if word in tagtoWord[tag]:
                        tagtoWord[tag][word] += 1
                    else:
                        tagtoWord[tag][word]  = 1

    '''Convert to probabilities'''
    for tag in tagList:
        total = 0
        for word in tagtoWord[tag]:
            total += tagtoWord[tag][word]

        for word in tagtoWord[tag]:
            tagtoWord[tag][word] = tagtoWord[tag][word]/total

    return (tagtoWord)

def tagSentence(splitSentence, tagList):
    '''tag a sentence with a given ordered list of tags
    '''

    result = ''
    if len(splitSentence) == len(tagList):
        for i in range(len(splitSentence)):
            result += splitSentence[i]+' '+tagList[i]+' '
    else:
        print('Error. Number of tags =/= number of tokens.')

    return result



def viterbi(sentence, tagList, twoTagDic, tagWord):
    ''' viterbi algorithm for POS tagging
    sentence == string; twoTagDic == dictionary [tag1][tag2] ==> p([tag3])
    tagWord == dictionary [tag] == > p([word])
    '''

    viterbiScores, backpointersMatrix = [{}], [{}]
    splitSentence = sentence.split()

    '''initialization'''

    backpointersMatrix[0]['*_*'] = 'inicio'

    for tagu in tagList:
        for tagd in tagList:
            pair = tagu+'_'+tagd
            viterbiScores[0][pair] = 0

    viterbiScores[0]['*_*'] = 0

    for k in range(1,len(splitSentence)+1):

        viterbiScores.append({})
        backpointersMatrix.append({})

        for tagu in tagList:
            for tagd in tagList:
                tagPair = tagu+'_'+tagd

                bestScore, bestTag = -float('inf'), None
                for tagt in tagList:
                    testValue = log(twoTagDic[tagt+'_'+tagu][tagd])
                    if viterbiScores[k-1][tagt+'_'+tagu]+testValue > bestScore:
                        #bestScore, bestTag = viterbiScores[k-1][tagt+'_'+tagu]*twoTagDic[tagt+'_'+tagu][tagd], tagt
                        bestScore, bestTag = viterbiScores[k-1][tagt+'_'+tagu]+testValue, tagt
                try:
                    viterbiScores[k][tagPair] = bestScore + log(tagWord[tagd][splitSentence[k-1]])
                except:                  #P(word|tag)==0
                    viterbiScores[k][tagPair] = -float('inf')
                backpointersMatrix[k][tagPair] = bestTag

    '''terminate'''

    value, finalPair = -float('inf'), None

    for tagu in tagList:
        for tagd in tagList:
            pair = tagu+'_'+tagd

            #print(viterbiScores[len(splitSentence)][pair])
            if viterbiScores[len(splitSentence)][pair] > value:
                value, finalPair = viterbiScores[len(splitSentence)][pair], pair

    if finalPair != None:
        lastWord, penulWord  = re.search('_.*', finalPair).group()[1:], re.search('.*_', finalPair).group()[:-1]
    else:
        print('Error')
        return([])

    tagged = []

    for i in range(len(splitSentence),0,-1):
        tagged.insert(0,lastWord)
        secondWord = backpointersMatrix[i][finalPair]
        lastWord   = re.search('.*_', finalPair).group()[:-1]
        finalPair = secondWord+'_'+secondWord

    return(tagged)

def HMMaccuracySentence(corpus, tagList, twoFreq, wordFreq):
    '''measure the accuracy of the HMM  (no of correct tags)
    twoFreq  == dictionary [tag1][tag2] ==> p([tag3])
    wordFreq == dictionary [tag] ==> p([word])
    '''

    total, correct = 0, 0
    broken         = 0

    for i in range(len(corpus)):

        control = True
        total += 1

        s = corpus[i]
        untag, comp_comstar = untagSentence(s)[0], untagSentence(s)[1]
        comp = []
        for c in comp_comstar:
            comp.append(c[1:])

        if len(untag.split())>0:

            vit = viterbi(untag, tagList, twoFreq, wordFreq)
            for t in range(len(comp)):
                try:
                    if vit[t] != comp[t]:
                        control = False
                except:
                    print('Broken sentence: ', vit, comp, t)
                    broken +=1

        if control:
            correct += 1
        #else:
        #    print('Incorrect tagging')
        #    print(comp)
        #    print(vit)

    print('%d broken sentences' % broken)
    return (correct/total)

def HMMaccuracy(corpus, tagList, twoFreq, wordFreq):
    '''measure the accuracy of the HMM  (no of correct tags)
    twoFreq  == dictionary [tag1][tag2] ==> p([tag3])
    wordFreq == dictionary [tag] ==> p([word])
    '''

    total, correct = 0,0
    broken         = 0   #store number of errors, i.e. missing tags or incomplete sentences

    for i in range(len(corpus)):
        s = corpus[i]
        untag, comp_comstar = untagSentence(s)[0], untagSentence(s)[1]
        comp = []
        for c in comp_comstar:
            comp.append(c[1:])

        if len(untag.split())>0:

            vit = viterbi(untag, tagList, twoFreq, wordFreq)
            for t in range(len(comp)):
                total += 1
                try:
                    if vit[t] == comp[t]:
                        correct += 1
                except:
                    broken +=1

    print('%d broken sentences' % broken)
    return (correct/total)


'''testes'''

if __name__ == '__main__':

    tagsCrude, tags  = open('tags.txt', 'r').readlines(), []
    for t in tagsCrude:
        tags.append(t.strip())

    corpus = open('mediumStar.txt', 'r').readlines()

    pairs  = twoFreq(corpus, tags)
    words =  wordFreq(corpus, tags)



    s = '" ⛬PONT Kika ⛬PROP " ⛬PONT , ⛬PONT de ⛬PRP Almodóvar ⛬PROP , ⛬PONT " ⛬PONT O=Sonho=Azul ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET chinês ⛬N Tian=Zhuangzhuang ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT A=Fraternidade=É=Vermelha ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP Krzystof=Kieslowski ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Amateur ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET americano ⛬N Hal=Hartley ⛬PROP , ⛬PONT com ⛬PRP Isabelle=Huppert ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Tempo=de=Viver ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET chinês ⛬N Zhang=Yimou ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Leni=Riefenstahl:=A=Deusa=Imperfeita ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET alemão ⛬N Ray=Mueller ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Xeque-Mate ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP Jim ⛬PROP McBride ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT 32=Variações=Sobre=Glenn=Gould ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET canadense ⛬ADJ François=Girard ⛬PROP ) ⛬PONT , ⛬PONT o ⛬DET hilariante ⛬ADJ " ⛬PONT Mamãe=É=de=Morte ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET americano ⛬N John=Waters ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT A=Rainha=Margot ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET francês ⛬N Patrice=Chéreau ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Kabloonak ⛬PROP " ⛬PONT ( ⛬PONT ficção ⛬N sobre ⛬PRP as ⛬DET filmagens ⛬N de ⛬PRP o ⛬DET clássico ⛬ADJ documentário ⛬N de ⛬PRP Robert=Flaherty ⛬PROP , ⛬PONT " ⛬PONT Nanook,=o=Esquimó ⛬PROP " ⛬PONT , ⛬PONT dirigida ⛬V por ⛬PRP o ⛬DET francês ⛬N Claude=Massot ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Comer=Beber=Viver ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP Ang ⛬PROP " ⛬PONT O=Banquete=de=Casamento=Lee ⛬PROP " ⛬PONT ) ⛬PONT , ⛬PONT " ⛬PONT A=Bronx=Tale ⛬PROP " ⛬PONT ( ⛬PONT primeiro ⛬ADJ filme ⛬N dirigido ⛬V por ⛬PRP Robert=De=Niro ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Barriga=de=Aluguel ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP a ⛬DET húngara ⛬N Marta=Meszaros ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Tigrero ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET finlandês ⛬N Mika=Kaurismaki ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT Prince=of=Jutland ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET dinamarquês ⛬N Gabriel=Axel ⛬PROP ) ⛬PONT , ⛬PONT " ⛬PONT The=Adventures=of=Priscilla ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP Stephen=Elliot ⛬PROP ) ⛬PONT e ⛬KC " ⛬PONT Kosh=ba=Kosh ⛬PROP " ⛬PONT ( ⛬PONT de ⛬PRP o ⛬DET tadjique ⛬N B.=Khudoynazarov ⛬PROP ) ⛬PONT . ⛬PONT '


    unt, tagged = untagSentence(s)
    print(unt.split(),'\n', tagged)

    #print(viterbi(unt, tags, pairs, words))
    print(HMMaccuracy(corpus, tags, pairs, words))
