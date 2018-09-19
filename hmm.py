import re
import pickle
import operator
import random

import viterbi as vit
import pre_proc as pp

'''functions for testing the models'''

def sliceCorpus(corCorpus, p): #slice corpus into 80-20 for dev + test. 0<p<100.
    dev, test = [], []

    for line in corCorpus:
        if random.SystemRandom().randint(0,100) > p:
            dev.append(line)
        else:
            test.append(line)

    return(dev, test)

def trainTest(dev, test, tagList, f, commondic='nenhum'): #train the HMM model and then test it

    if   f == 'HMM':
        pairs  = vit.twoFreq(dev, tagList)
        words =  vit.wordFreq(dev, tagList)
        return (vit.HMMaccuracy(test, tagList, pairs, words))
    elif f == 'common':
        common = pp.likelyTag(dev)
        return(pp.tagAccuracy(test, common))


def nfoldValidation(corCorpus, tagList, n, p, f='HMM'):  #='HMM'): #checar sintaxe

        totalAccuracy = 0

        for i in range(n):
            sliced = sliceCorpus(corCorpus, p)
            dev, test = sliced[0], sliced[1]

            print('LEN',len(dev),len(test))

            totalAccuracy += trainTest(dev, test, tagList, f)

        return (totalAccuracy/n)






'''testes'''

'''itens para os testes'''
corpusTodo = open('cetenLimpo.txt', 'r').readlines()
tags       = open('tags', 'r').readlines()
dev        = open('pequenoCorrigido.txt', 'r').readlines()

'''funcoes'''
print('HMM: ',nfoldValidation(dev, tags, 2, 2,'HMM'))
print('common: ',nfoldValidation(dev, tags, 2,2, 'common'))
