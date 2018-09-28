import re
import pickle
import operator
import random

def listTags(corCorpus):
    '''generate a list with all tags. input is the already clean corpus
    '''

    l, tagList = [], open('tagList.txt', 'w')
    for line in corCorpus:
        splitSentence = line.split()
        for s in splitSentence:
            if s[0] == '⛬' and not(s in l):
                l.append(s)
                tagList.write(s+'\n')


def corpusToSentence(corpus):
    '''clean the corpus. Output is a file named by the user.
    each line is a tagged sentence in the following format:
    word1 ⛬TAG1 word2 ⛬TAG2
    '''

    corpusName = input('Nome do arquivo do corpus de sentencas: ')
    newCorpus = open(corpusName+'.txt', 'w')

    regexWord = '^.*?\s'
    regexTag = '\s(N|PROP|SPEC|DET|PERS|ADJ|ADV|V|NUM|PRP|KS|KC|IN|EC)\s'
    newSentence = True


    for line in corpus:
        if line == '\n' and newSentence: #detecs sentence end
            newCorpus.write('\n')
            newSentence = False          #avoid creating empty lines

        elif line[0]=='$':

            newSentence = True
            word = line[1]
            tag  = 'PONT'

            newCorpus.write(word+' ⛬'+tag+' ')

        elif line[0]!='<':

            newSentence = True
            word = re.search(regexWord, line)
            tag =  re.search(regexTag,  line)

            try:
                newCorpus.write(word.group()[:-1]+' ⛬'+tag.group()[1:-1]+' ')
            except:
                pass

    newCorpus.close()

def numTag(corCorpus):
    '''count no of tags
    '''

    total = 0
    for line in corCorpus:
        words = line.split()
        for w in words:
            if w[0] == '⛬':
                total += 1
    return total

def counTag(corCorpus):
    '''count no of  occurence for each tag.
    Output into a txt file, named by the user.
    '''

    noTag = dict() #dictionary w tags as keys and no occurrence as value

    fileName = input('Nome do arquivo para contagem de TAGs: ')
    newFile  = open(fileName+'.txt', 'w')

    for line in corCorpus:
        tags = re.findall('⛬\w*', line)

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



def likelyTag(corCorpus):
    '''generate a dictionary [words] ==> [likely tag].
    '''
    wordDict = dict()

    for line in corCorpus:
        words = line.split()

        for n in range(0,len(words),2):
            if n+1 < len(words):
                if words[n] in wordDict:
                    if words[n+1] in wordDict[words[n]]:
                        wordDict[words[n]][words[n+1]] += 1
                    else:
                        wordDict[words[n]][words[n+1]] = 1
                else:
                    wordDict[words[n]] = {words[n+1] : 1}

    for word in wordDict:
        wordDict[word] = max(wordDict[word].items(), key=operator.itemgetter(1))[0]

    return (wordDict)


def cutCorpus(corCorpus, n=10000):
    '''cut the corpus into a small file for testing stuff.
    saves it into a file named smallCorpus.
    '''

    newCorpus = open('smallCorpus.txt', 'w')

    for i in range(n):
        newCorpus.write(corCorpus[i])

    newCorpus.close()


def maxTag(sentence, commonDictionary):
    '''Tag a sentence with most likely tag method.
    commonDictionary == dictionary [word] ==> most likely tag.
    '''


    newSentence = sentence.split()
    tagged      = []

    for word in newSentence:

        try:
            tagged.append(commonDictionary[word])
        except:
            tagged.append('⛬DESCONHECIDO')

    return(tagged)


def tagAccuracy(corCorpus, commonDictionary):
    '''tag sentences with commonest tag. Calculate the percentage of correct tags.
    commonDictionary == dictionary [word] ==> most likely tag.
    '''

    correct, total = 0,0

    for line in corCorpus:
        sentence, correctTags = '', []
        wordlist = line.split()
        for w in wordlist:
            if w[0] != '⛬':
                sentence += w+' '
            else:
                correctTags.append(w)

        tagged = maxTag(sentence, commonDictionary) #calculate the tags

        for w in range(0, len(tagged)):       #count correct guesses
            total += 1
            if correctTags[w] == tagged[w]:
                correct += 1

    return (correct/total)


def tagAccuracySentence(corCorpus, commonDictionary):
    '''tag sentences with commonest tag. Calculate the percentage of correct tagged sentences.
    '''

    correct, total = 0,0

    for line in corCorpus:

        total += 1
        correctTagging = True

        sentence, correctTags = '', []
        wordlist = line.split()
        for w in wordlist:
            if w[0] != '⛬':
                sentence += w+' '
            else:
                correctTags.append(w)

        tagged = maxTag(sentence, commonDictionary) #calculate the tags

        for w in range(0, len(tagged)):       #count correct guesses
            if correctTags[w] != tagged[w]:
                correctTagging = False
        if correctTagging:
            correct += 1

    return (correct/total)



def countWords(corCorpus):

    wordic, size = dict(), 0
    wordFreq     = open('wordFreq', 'wb')

    for sentence in corCorpus:
        for word in sentence.split():
            if word[0] != '⛬':
                size += 1
                if word in wordic:
                    wordic[word] += 1
                else:
                    wordic[word] = 1

    print(wordic)
    print(wordic['a'])
    print(size)
    pickle.dump(wordic, wordFreq)

def noEmptylines(corCorpus):
    new_corpus = open(input('Nome do novo arquivo: '), 'w')
    noEmptylines = 0
    for i in corCorpus:
        if i != '\n':
            new_corpus.write(i+'\n')
        else:
            noEmptylines += 1
    new_corpus.close()
    print(noEmptylines)


def findProblems(corCorpus):

    throw = 0

    for sentence in corCorpus:
        noTag, noWord = 0, 0
        sliced = sentence.split()

        for tw in sliced:
            if tw[0] == '⛬':
                noTag += 1
            else:
                noWord +=1

        if noTag != noWord:
            print(sliced)
            throw += 1

    print(throw)



'''testes'''
if __name__ == '__main__':

    corpus = open('cleanCorpus.txt', 'r').readlines()
    common = likelyTag(corpus)

    cutCorpus(corpus)

    print(tagAccuracySentence(corpus, common))

    print(len(corpus))
