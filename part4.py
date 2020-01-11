from part2 import estimateEmissionParameters
from part3 import estimateTransitionParameters, get_sentences
import argparse



def kth_best_viterbi(devFilePath, sentence, k):
    emissionParameters, observations = estimateEmissionParameters(trainFilePath)
    transitionParameters, tags = estimateTransitionParameters(trainFilePath)
    print(emissionParameters)
    
    tags = list(tags.keys())
    tags.remove("START")
    tags.remove("STOP")
    #initialize scores array
    scores = []
    for i in range(len(tags)):
        row = []
        for j in range(len(sentence)):
            row.append([])
        scores.append(row)
        
    #initialize paths array
    # paths = []
    # for i in range(len(tags)):
    #     row = []
    #     for j in range(len(sentence)):
    #         row.append([])
    #     paths.append(row)
    
    #STORE POINTER TO PATHS IN SCORE INSTEAD
        

    for i in range(len(sentence)):
        if sentence[i] not in observations:
            sentence[i] = "#UNK#"
    
    #first word
    for i in range(len(tags)):
        score = 1 * transitionParameters.get(("START", tags[i]), 0) * emissionParameters.get((tags[i], sentence[0]), 0)
        path = [tags[i]]
        scores[i][0].append((score, path))
        # paths[i][0].append([tags[i]])    

    for j in range(1, len(sentence)):
        currentWord = sentence[j]
        for i in range(len(tags)):
            currentTag = tags[i]
            for u in range(len(tags)):
                prevTag = tags[u]
                for t in range(len(scores[i][j-1])):
                    score = scores[u][j-1][t][0] * transitionParameters.get((prevTag, currentTag), 0) * emissionParameters.get((currentTag, currentWord), 0)
                    path = scores[u][j-1][t][1] + [currentTag]
                    #paths[i][j].append(paths[u][j-1][t] + [currentTag])

                    scores[i][j].append((score, path))
                    # scores[i][j].append(score)
            
            #sort scores[i][j] and take top 7
            #sort by score in descending order
            scores[i][j].sort(key = lambda f: f[0], reverse=True)
            scores[i][j] = scores[i][j][:k] #take the k best
                
    #STOP
    finalScores = []
    for u in range(len(tags)):
        prevTag = tags[u]
        for t in range(len(scores[u][len(sentence)-1])):
            score = scores[u][len(sentence)-1][t][0] * transitionParameters.get((prevTag, "STOP"), 0)
            path = scores[u][len(sentence)-1][t][1]
            finalScores.append((score, path))

    #sort and slice
    finalScores.sort(key = lambda f: f[0], reverse=True)
    finalScores = finalScores[:k]
    # print(finalScores[6])    
    # print(scores[0][18])
    # print(finalScores[0][1])
    # print(finalScores[k-1][1])
    return finalScores[k-1][1]
    

def writeOutputToFile(devFilePath):
    results = []
    sentences = get_sentences(devFilePath)
    count = 0
    for sentence in sentences:
        tagSequence = kth_best_viterbi(devFilePath, sentence, 7)
        count+=1
        print(f'{count}/{len(sentences)}')
        print(tagSequence)
        results.append(tagSequence)
        

    with open("dev.p4.out", "w", encoding="utf-8") as outputFile:
        for i in range(len(results)):
            for j in range(len(results[i])):
                outputFile.write(f'{sentences[i][j]} {results[i][j]}\n')
            outputFile.write('\n')    
            
                
    
    # print(results)
    return 
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, dest='dataset', required=True, help='enter dataset')
    args = parser.parse_args()
    trainFilePath = f'../{args.dataset}/{args.dataset}/train'
    devFilePath = f'../{args.dataset}/{args.dataset}/dev.in'
    
    sentence = get_sentences(devFilePath)[0]
    kth_best_viterbi(devFilePath, sentence, 7)
    # print(sentence)
    # writeOutputToFile(devFilePath)