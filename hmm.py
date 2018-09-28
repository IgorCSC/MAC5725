import re
import pickle
import operator
import random
import time
import argparse

import viterbi as vit
import pre_proc as pp

'''input parser'''
parser = argparse.ArgumentParser(
    description='Example with nonoptional arguments',
)

parser.add_argument('corpus', action="store", nargs='?', type=str, default='cleanCorpus.txt')
parser.add_argument('method', action="store", nargs='?', type=str, default='HMM')
parser.add_argument('split', action="store", nargs='?', type=int, default=20)
parser.add_argument('nfold', action="store", nargs='?', type=int, default=1)

args = parser.parse_args()

if args.method not in ['HMM', 'common', 'commonAll']:
    print('Invalid method. Please choose one of the following: hmm, common, commonAll.')
    quit()
if args.split < 0 or args.split > 100:
    print('Invalid split size. Please chosse 0 < n < 100.')
    quit()




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

        theStart = time.perf_counter() #timer to track the entire nfold

        totalAccuracy = 0

        for i in range(n):

            startTime = time.perf_counter()
            print('\niteration %d ' % (i+1))

            sliced = sliceCorpus(corCorpus, p)
            dev, test = sliced[0], sliced[1]

            print('Training time', time.perf_counter()-startTime)
            print('Corpus` size: %d sentences in DEV and %d sentences in TEST. ' % (len(dev),len(test)))
            startTime = time.perf_counter()
            itAccuracy = trainTest(dev, test, tagList, f)
            totalAccuracy += itAccuracy
            print('Evaluation time =', time.perf_counter()-startTime)
            print('Iteration accuracy:', itAccuracy)

        print('\nTotal time = {0} minutes'.format((time.perf_counter()-theStart)/60))


        return (totalAccuracy/n)



'''main routine'''


'''testes'''

'''itens para os testes'''
#corpusTodo = open('cleanCorpus.txt', 'r').readlines()
tagsCrude, tags  = open('tags.txt', 'r').readlines(), []
for t in tagsCrude:
    tags.append(t.strip())
#dev        = open('mediumStar.txt', 'r').readlines()
corpus     = open(args.corpus, 'r').readlines()

'''funcoes'''
print('\n%s accuracy in %d excecutions is:' % (args.method, args.nfold),nfoldValidation(corpus, tags, args.nfold, args.split, args.method))
#print('common: ',nfoldValidation(corpusTodo, tags, 1,20, 'commonAll'))
