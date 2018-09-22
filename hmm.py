import re
import pickle
import operator
import random

import viterbi as vit
import pre_proc as pp

'''functions for testing the models'''

def sliceCorpus(corCorpus, p):
    '''slice corpus into 100-p/p for dev + test. 0<p<100.
    '''

    dev, test = [], []

    for line in corCorpus:
        if random.SystemRandom().randint(0,100) > p:
            dev.append(line)
        else:
            test.append(line)

    return(dev, test)

def trainTest(dev, test, tagList, f, commondic='nenhum'):
    '''train the HMM model and then test it.
    dev&test==sliced corpus. tagList == list of all possible tags. f == algorithm tested (hmm or common)
    commondic == in 'most likely tag' method, a dictonary [word] ---> likely tag.
    '''


    if   f == 'HMM':
        pairs  = vit.twoFreq(dev, tagList)
        words =  vit.wordFreq(dev+test, tagList) #train word emission in all words to avoid unseen vocab.
        return (vit.HMMaccuracy(test, tagList, pairs, words))
    elif f == 'common':
        common = pp.likelyTag(dev)
        return(pp.tagAccuracy(test, common))
    elif f == 'commonAll':
        common = pp.likelyTag(dev+test)
        return(pp.tagAccuracy(test,common))


def nfoldValidation(corCorpus, tagList, n, p, f='HMM'):
        '''n-fold validation
        n == number of tests; p == dev test split proportion (e.g. 20 splits in 80dev 20test)
        f == algorithm to be tested. HMM or common (most likely tag)
        '''

        totalAccuracy = 0

        for i in range(n):
            sliced = sliceCorpus(corCorpus, p)
            dev, test = sliced[0], sliced[1]

            print('LEN',len(dev),len(test))

            totalAccuracy += trainTest(dev, test, tagList, f)

        return (totalAccuracy/n)






'''testes'''

'''itens para os testes'''
corpusTodo = open('cleanCorpus.txt', 'r').readlines()
tagsCrude, tags  = open('tags.txt', 'r').readlines(), []
for t in tagsCrude:
    tags.append(t.strip())
dev        = open('mediumStar.txt', 'r').readlines()

'''funcoes'''
print('HMM: ',nfoldValidation(corpusTodo, tags, 1, 20,'HMM'))
#print('common: ',nfoldValidation(corpusTodo, tags, 1,20, 'commonAll'))
