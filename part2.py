import argparse



def estimateEmissionParameters(trainingFile):
    tags = {} #y
    observations = {} #o
    emission_count = {} #y -> o
    estimates = {}
    # with open(trainingFile, 'r', encoding="utf-8") as f:
    #     for line in f.readlines():
    #         currentLine = line.strip().split()
    #         if line == '\n': #empty line
    #             continue
    #         observation = currentLine[0]
    #         tag = currentLine[1]
    #         observations[observation] = observations.get(observation, 0) + 1
    #         emission_count[(tag,observation)] = emission_count.get((tag,observation), 0) + 1
    #         tags[tag] = tags.get(tag, 0) + 1
    
    data = smoothing(trainingFile, 3)
    for currentLine in data:
        observation = currentLine[0]
        tag = currentLine[1]
        observations[observation] = observations.get(observation, 0) + 1
        emission_count[(tag,observation)] = emission_count.get((tag,observation), 0) + 1
        tags[tag] = tags.get(tag, 0) + 1

    #getting estimates for emission parameters
    
    
    for (tag, observation) in emission_count:
        estimates[(tag, observation)] = emission_count[(tag,observation)] / tags[tag]
        
    return estimates, observations
    
    
def smoothing(trainingFile, k):
    new_data = []
    tags = {} #y
    observations = {} #o
    emission_count = {} #y -> o
    words_less_than_k = set()
    with open(trainingFile, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            currentLine = line.strip().split()
            if line == '\n': #empty line
                continue
            observation = currentLine[0]
            tag = currentLine[1]
            observations[observation] = observations.get(observation, 0) + 1
            emission_count[(tag,observation)] = emission_count.get((tag,observation), 0) + 1
            tags[tag] = tags.get(tag, 0) + 1
    
    for key in observations:
        if observations[key] < k:
            words_less_than_k.add(key)
    
    with open(trainingFile, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            currentLine = line.strip().split()
            if line == '\n': #empty line
                continue
            observation = currentLine[0]
            tag = currentLine[1]
            new_list = []
            if observation in words_less_than_k:
                new_list.append('#UNK#')
                new_list.append(tag)
                new_data.append(new_list)
            else:
                new_data.append(currentLine)
    return new_data
    
    
    
    
    
    
def simple_sentiment_analysis(devFilePath):
    emissionParameters, observations = estimateEmissionParameters(trainFilePath)
    with open(devFilePath, 'r', encoding="utf-8") as f:
        with open('dev.p2.out', 'w', encoding="utf-8") as outputFile:
            for line in f.readlines():
                currentLine = line.strip().split()
                if line == '\n': #empty line
                    outputFile.write("\n")
                    continue
                obs = currentLine[0]
                if obs not in observations: #word not found in training set
                    predictedTag = None
                    maxEmissionScore = 0
                    for tag,observation in emissionParameters:
                        if observation == "#UNK#" and emissionParameters[(tag,observation)]>maxEmissionScore:
                            predictedTag = tag
                            maxEmissionScore = emissionParameters[(tag, observation)]
                    outputFile.write(f'#UNK# {predictedTag}\n')
                else:
                    predictedTag = None
                    maxEmissionScore = 0
                    for tag,observation in emissionParameters:
                        if observation == obs and emissionParameters[(tag,observation)]>maxEmissionScore:
                            predictedTag = tag
                            maxEmissionScore = emissionParameters[(tag, observation)]
                    outputFile.write(f'{obs} {predictedTag}\n')
            
    return
    
    
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, dest='dataset', required=True, help='enter dataset')
    args = parser.parse_args()
    trainFilePath = f'../{args.dataset}/{args.dataset}/train'
    devFilePath = f'../{args.dataset}/{args.dataset}/dev.in'

    # m_training, estimates = estimateEmissionParameters(trainFilePath)


    # estimateEmissionParameters(trainFilePath)
    # smoothing(trainFilePath, 3)
    simple_sentiment_analysis(devFilePath)