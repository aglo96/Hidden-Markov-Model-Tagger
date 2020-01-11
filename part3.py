import argparse
from part2 import estimateEmissionParameters


def estimateTransitionParameters(trainingFile):
    transitionParameters = {}
    transitions = {}
    tags = {}
    
    with open(trainingFile, "r", encoding="utf-8") as f:
        prevTag = "START"
        for line in f.readlines():
            currentLine = line.strip().split()
            if line == "\n": #end of a sentence. Last line of the file is a newline!
                tags["STOP"] = tags.get("STOP", 0) + 1
                transitions[(prevTag, "STOP")] = transitions.get((prevTag, "STOP"), 0) + 1
                prevTag = "START"    
            else:
                currTag = currentLine[1]
                if prevTag == 'START':
                    tags["START"] = tags.get("START",0) + 1 
                tags[currTag] = tags.get(currTag,0) + 1
                transitions[(prevTag, currTag)] = transitions.get((prevTag, currTag), 0) + 1
                prevTag = currTag     
    
     
    for prevTag, currTag in transitions:
        transitionParameters[(prevTag, currTag)] = transitions.get((prevTag, currTag))/tags[prevTag]
    
    return transitionParameters, tags



def get_sentences(devFilePath):
    sentences = []
    with open(devFilePath, "r", encoding="utf-8") as f:
        sentence = []
        for line in f.readlines():
            currentLine = line.strip().split()
            if line == '\n':
                sentences.append(sentence)
                sentence = []
            else:
                sentence.append(currentLine[0])
    return sentences
    

def viterbi(devFilePath):
    transitionParameters, tags = estimateTransitionParameters(trainFilePath)
    emissionParameters, observations = estimateEmissionParameters(trainFilePath)
    tags = list(tags.keys())
    tags.remove("START")
    tags.remove("STOP")
    numberOfTags = len(tags) #excluding START and STOP
    sentences = get_sentences(devFilePath)
    
    results = []
    for sentence in sentences:
        for i in range(len(sentence)):
            if sentence[i] not in observations:
                sentence[i] = '#UNK#'
        
        #initialize 2D array for scores
        scores = []
        for i in range(numberOfTags):
            layer = []
            for j in range(len(sentence)):
                layer.append(0)
            scores.append(layer)

        #first word
        for i in range(len(tags)):
            scores[i][0] = 1 * transitionParameters.get(("START", tags[i]), 0) * emissionParameters.get((tags[i], sentence[0]), 0) 
        
        #remaining words
        for j in range(1, len(sentence)):
            currentWord = sentence[j]
            for i in range(numberOfTags):
                currentTag = tags[i] 
                for u in range(numberOfTags):
                    prevTag = tags[u]
                    scores[i][j] = max(scores[i][j], scores[u][j-1] * transitionParameters.get((prevTag, currentTag), 0) * emissionParameters.get((currentTag, currentWord), 0))
                
        #stop state
        finalScore = 0
        for i in range(numberOfTags):
            finalScore = max(finalScore, scores[i][len(sentence)-1] * transitionParameters.get((tags[i], "STOP"), 0))
            
        #perform backtracking to get optimum tags
        optimumTags = []
        next_y = "STOP"
        for j in range(len(sentence)-1, -1, -1):
            y = None
            maxScore = 0
            for i in range(numberOfTags):
                if scores[i][j] * transitionParameters.get((tags[i],next_y), 0) >= maxScore:
                    maxScore = scores[i][j] * transitionParameters.get((tags[i],next_y), 0)
                    y = tags[i]
            optimumTags.append(y)
            next_y = y
        optimumTags.reverse()        
        results.append(optimumTags)
        
    return results


def writeResultsToFile(devFilePath):
    sentences = get_sentences(devFilePath)
    results = viterbi(devFilePath)
    with open("dev.p3.out", "w", encoding="utf-8") as outputFile:
        for i in range(len(results)):
            for j in range(len(results[i])):
                outputFile.write(f'{sentences[i][j]} {results[i][j]}\n')
            outputFile.write('\n')
    return
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, dest='dataset', required=True, help='enter dataset')
    args = parser.parse_args()
    trainFilePath = f'../{args.dataset}/{args.dataset}/train'
    devFilePath = f'../{args.dataset}/{args.dataset}/dev.in'

    writeResultsToFile(devFilePath)
    




