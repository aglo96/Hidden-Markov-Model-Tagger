def trainTagger(dataset,k):
    return EstimateEmission(dataset,k)

def testTagger(emissionParameters,dataset,output_file_path):
    
    outputFile = open(output_file_path,'w')
    
    with open(dataset) as f:
        
        unknown = '#UNK#'
        for line in f.readlines():
            x = line.strip()
            
            if len(x)>0:
                if x in emissionParameters:
                    outputFile.write(f"{x} {max(emissionParameters[x],key=emissionParameters[x].get)}\n")
                else:
                    outputFile.write(f"{x} {max(emissionParameters[unknown],key=emissionParameters[unknown].get)}\n")
            else:
                outputFile.write("\n")
                
def evaluateTagger(test_results_file,validation_file):
    testResults = open(test_results_file,'r').readlines()
    validationResults = open(validation_file,'r').readlines()
    
    devZip = zip(testResults,validationResults)
    
    print(list(devZip))
    
    
    
    
def getTrigramLambda(transitionCounts,counts):
    # set )%1 ---- )%2 = )%3 = 0
    lambdaUno = 0
    lambdaDuo = 0
    lambdaTri = 0

    # foreach trigram tl,t2,t3 with f(tl,t2,t3) > 0
    for transitions in transitionCounts['Trigrams']:
        y1,y2,y3 = transitions
        if (transitionCounts['Bigrams'][(y1,y2)]-1)==0:
            caseLambdaTri = 0
        else:
            caseLambdaTri = (transitionCounts['Trigrams'][transitions]-1)/(transitionCounts['Bigrams'][(y1,y2)]-1)
        if (transitionCounts['Unigrams'][(y2)]-1)==0:
            caseLambdaDuo = 0
        else:
            caseLambdaDuo = (transitionCounts['Bigrams'][(y2,y3)]-1)/(transitionCounts['Unigrams'][(y2)]-1)
        if (counts['Unigrams']-1)==0:
            caseLambdaUno = 0
        else:
            caseLambdaUno = (transitionCounts['Unigrams'][y3]-1)/(counts['Unigrams']-1)

        cases = [caseLambdaUno,caseLambdaDuo,caseLambdaTri]
        # depending on the maximum of the following three values:

        casesMax = max(cases)

        # case f(h,t2)-I " increment )%3 by f(tl,t2,t3)
        if casesMax!=0:
            if casesMax == cases[2]:
                lambdaTri += transitionCounts['Trigrams'][transitions]
            elif casesMax == cases[1]:
                lambdaDuo += transitionCounts['Trigrams'][transitions]
            elif casesMax == cases[0]:
                lambdaUno += transitionCounts['Trigrams'][transitions]
                
    lambdaDuo *= 1.05
    lambdas = [lambdaUno,lambdaDuo,lambdaTri]
    totalLambdaCounts = sum([lambdaUno,lambdaDuo,lambdaTri])
    return [lambdaparam/totalLambdaCounts for lambdaparam in lambdas]

    




def TnTViterbi(devin,emissionParams,transitionParams,devOutput):
    transitionParams,lambdas = transitionParams
    outputFile = open(devOutput,'w')
    
    with open(devin) as f:
        devText = f.read()
        
        #Assuming that sentnces are separated by a double line break
        sentences = devText.split('\n\n')

        sentences = [sentence for sentence in sentences if len(sentence)>0]

        
        for sentence in sentences:
            sentenceWords = sentence.split('\n')
            score = 1
            wordScores = []

            for wordIndex in range(len(sentenceWords)):
                word = sentenceWords[wordIndex]
                tagScores = {}
                if word in emissionParams:
                    wordEmission = emissionParams[word]
                else:
                    wordEmission = emissionParams['#UNK#']
                    
                if wordIndex == 0:
                    for tag in wordEmission:
                        transition = ('START',tag)
                        if transition in transitionParams['Bigrams']:
                            tagTransition = transitionParams['Bigrams'][transition]
                        else:
                            tagTransition = 0
                        tagScores[tag]=score*wordEmission[tag]*tagTransition
                        
                    wordScores.append(tagScores)
                    
                elif wordIndex > 0:
                    prevWordTags = wordScores[wordIndex-1]

                    if wordIndex > 1:
                        previousPreviousWordTags = wordScores[wordIndex-2]
                    else:
                        previousPreviousWordTags = 'START'

                    for tag in wordEmission:
                        PrevTagToThisTagScores = []
                        for previousTag in prevWordTags:
                            if previousPreviousWordTags == 'START':
                                previousPreviousTag = 'START'
                                previousScore = prevWordTags[previousTag]
                                if tag in transitionParams['Unigrams']:
                                    uniTransition = transitionParams['Unigrams'][tag]
                                else:
                                    uniTransition = 0

                                bigram = (previousTag,tag)
                                trigram = (previousPreviousTag,previousTag,tag)

                                if bigram in transitionParams['Bigrams']:
                                    biTransition = transitionParams['Bigrams'][bigram]
                                else:
                                    biTransition = 0

                                if trigram in transitionParams['Trigrams']:
                                    triTransition = transitionParams['Trigrams'][trigram]
                                else:
                                    triTransition = 0

                                tagTransition = lambdas[0]*uniTransition + lambdas[1]*biTransition + lambdas[2]*triTransition
                                PrevTagToThisTagScores.append(previousScore*wordEmission[tag]*tagTransition)
                            else:
                                for previousPreviousTags in previousPreviousWordTags:
                                    previousPreviousTag = previousPreviousTags
                                    previousScore = prevWordTags[previousTag]
                                    if tag in transitionParams['Unigrams']:
                                        uniTransition = transitionParams['Unigrams'][tag]
                                    else:
                                        uniTransition = 0

                                    bigram = (previousTag,tag)
                                    trigram = (previousPreviousTag,previousTag,tag)

                                    if bigram in transitionParams['Bigrams']:
                                        biTransition = transitionParams['Bigrams'][bigram]
                                    else:
                                        biTransition = 0

                                    if trigram in transitionParams['Trigrams']:
                                        triTransition = transitionParams['Trigrams'][trigram]
                                    else:
                                        triTransition = 0

                            
                                    tagTransition = lambdas[0]*uniTransition + lambdas[1]*biTransition + lambdas[2]*triTransition
                                    PrevTagToThisTagScores.append(previousScore*wordEmission[tag]*tagTransition)
                        
                        tagScores[tag]=max(PrevTagToThisTagScores)
                    wordScores.append(tagScores)
            
            stopTagScores = []
            
            for previousTag in wordScores[-1]:
                previousScore = wordScores[-1][previousTag]
                transition = (previousTag,'STOP')
                if transition in transitionParams['Bigrams']:
                    tagTransition = transitionParams['Bigrams'][transition]
                else:
                    tagTransition = 0
                    
                stopTagScores.append(previousScore*tagTransition)
            wordScores.append(max(stopTagScores))
            
#             Backward Algorithm
            
            bestTags = []

            if len(wordScores)-1<=2:
                for i in range(len(wordScores)-1,0,-1):
                    if i == len(wordScores)-1:
                        for tags in wordScores[i-1]:
                            transition = (tags,'STOP')
                            if transition in transitionParams['Bigrams']:
                                tagTransition = transitionParams['Bigrams'][transition]
                            else:
                                tagTransition = 0
                            if wordScores[i-1][tags]*tagTransition == wordScores[i]:
                                bestTags.append(tags)
                    
                    elif i < len(wordScores)-1:
                        bestTagCompetition = {}
                        for tags in wordScores[i-1]:
                            transition = (tags,bestTags[0])
                            if transition in transitionParams['Bigrams']:
                                tagTransition = transitionParams['Bigrams'][transition]
                            else:
                                tagTransition = 0
                            
                            bestTagCompetition[tags]=(wordScores[i-1][tags]*tagTransition)
                            
                        bestTags.insert(0,max(bestTagCompetition,key=bestTagCompetition.get))
            else:
                for i in range(len(wordScores)-1,1,-1):
                        
                    if i == len(wordScores)-1 and len(wordScores)-1>2:
                        for tags in wordScores[i-1]:
                            transition = (tags,'STOP')
                            if transition in transitionParams['Bigrams']:
                                tagTransition = transitionParams['Bigrams'][transition]
                            else:
                                tagTransition = 0
                            if wordScores[i-1][tags]*tagTransition == wordScores[i]:
                                bestTags.append(tags)
                    
                    elif i < len(wordScores)-1 and i > 2:
                        bestTagCompetition = {}
                        for tags in wordScores[i-1]:
                            for previousTags in wordScores[i-2]:
                                unigram = bestTags[0]
                                bigram = (tags,bestTags[0])
                                trigram = (previousTags,tags,bestTags[0])

                                if unigram in transitionParams['Unigrams']:
                                    uniTransition = transitionParams['Unigrams'][unigram]
                                else:
                                    uniTransition = 0

                                if bigram in transitionParams['Bigrams']:
                                    biTransition = transitionParams['Bigrams'][bigram]
                                else:
                                    biTransition = 0

                                if trigram in transitionParams['Trigrams']:
                                    triTransition = transitionParams['Trigrams'][trigram]
                                else:
                                    triTransition = 0

                                tagTransition = lambdas[0]*uniTransition + lambdas[1]*biTransition + lambdas[2]*triTransition
                                
                                if tags not in bestTagCompetition:
                                    bestTagCompetition[tags]=0
                                    # We calculate the highest probable transition from the previous 2 pair of tags and we take the latter of the pair as the next best node
                                if (wordScores[i-1][tags]*tagTransition)>bestTagCompetition[tags]: 
                                    bestTagCompetition[tags]=(wordScores[i-1][tags]*tagTransition)
                        
                            
                        bestTags.insert(0,max(bestTagCompetition,key=bestTagCompetition.get))
                    elif i == 2:
                        bestTagCompetition = {}
                        for tags in wordScores[i-1]:
                            for previousTags in wordScores[i-2]:
                                unigram = bestTags[0]
                                bigram = (tags,bestTags[0])
                                trigram = (previousTags,tags,bestTags[0])

                                if unigram in transitionParams['Unigrams']:
                                    uniTransition = transitionParams['Unigrams'][unigram]
                                else:
                                    uniTransition = 0

                                if bigram in transitionParams['Bigrams']:
                                    biTransition = transitionParams['Bigrams'][bigram]
                                else:
                                    biTransition = 0

                                if trigram in transitionParams['Trigrams']:
                                    triTransition = transitionParams['Trigrams'][trigram]
                                else:
                                    triTransition = 0

                                tagTransition = lambdas[0]*uniTransition + lambdas[1]*biTransition + lambdas[2]*triTransition
                                

                                if (previousTags,tags) not in bestTagCompetition:
                                    bestTagCompetition[(previousTags,tags)]=0
                                    # We calculate the highest probable transition from the previous 2 pair of tags and we take the latter of the pair as the next best node
                                if (wordScores[i-1][tags]*tagTransition)>bestTagCompetition[(previousTags,tags)]: 
                                    bestTagCompetition[(previousTags,tags)]=(wordScores[i-1][tags]*tagTransition)
                        
                        bestFirstTag,bestSecondTag = max(bestTagCompetition,key=bestTagCompetition.get)
                        bestTags.insert(0,bestSecondTag)
                        bestTags.insert(0,bestFirstTag)

            for i in range(len(sentenceWords)):
                outputFile.write(f"{sentenceWords[i]} {bestTags[i]}\n")
            outputFile.write('\n')
            
