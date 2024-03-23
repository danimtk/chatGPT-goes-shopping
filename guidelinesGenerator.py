import util.OpenAIRequest as oair

'''
In order to prepare the experiments with LLM-generated, two steps are required:
    1. Write a prompt that will be used to generate the guideline
    2. Request the LLM to generate the guideline using resulting prompt from step 1
    3. Edit the guideline to add the message that requests the model to annotate the given tuple and ten examples of annotaded tuples (for experiment with +few-shot)

The function generatePrompt(annotatedTuples, dataset, storeType) executes step 1 by creating a text file with the prompt that will be used to generate the guideline.
    annotatedTuples: dataframe of annotated tuples (query, product, label)
    dataset: string that identifies the experiment (e.g. "WANDS", "Pharma") and names the resulting file in the format "prompt_{dataset}.txt"
    storeType: string that identifies the type of store (e.g. "furniture and deco", "pharmacy")

The function generateGuideline(resultPromptFilepath, model, dataset) executes step 2 by requesting the LLM to generate the guideline using the prompt created in step 1.
    resultPromptFilepath: string that identifies the file containing the prompt to be read
    model: string that identifies the LLM model to be used (e.g. "gpt-4", "gpt-3.5-turbo")
    dataset: string that identifies the experiment (e.g. "WANDS", "Pharma") and names the resulting file in the format 'LLM-generated_guideline_{dataset}.txt'
'''

def generatePrompt(annotatedTuples, dataset, storeType):
    listTuples = []

    for _, row in annotatedTuples.iterrows():
        listTuples.append((row['query'], row['name'], row['label']))

    with open(f'data/prompts_for_guideline_generation/prompt_{dataset}.txt', 'w', encoding="utf-8") as resultPrompt:

        for item in listTuples:
            resultPrompt.write("%s\n" % str(item))

        # In our experiments the storeType was "furniture and deco" for WANDS dataset and "pharmacy" for Pharma dataset

        resultPrompt.write(f"Given the examples of queries and products from a {storeType} store in the format (query,product,label), create a guideline that explains to a human annotator how to label products as 'Relevant' or 'Not relevant' based on the relationships between the query and the returned product. Disregard typos in queries and remember, the goal is to match the user's intent, not necessarily the exact words in the query. Consider the context and the likely intent behind the query when deciding whether a product is Relevant or Not relevant. Describe some characteristics and examples of each label.")
        
    resultPrompt.close()


def generateGuideline(resultPromptFilepath, model, dataset):    
    with open(resultPromptFilepath, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        content = '\r'.join(lines)
        clean_content = content.replace('\n','')
    prompt = repr(clean_content)

    modelRequest = oair.OpenAIRequest()

    #pergunta: nesse caso content do user é vazio, podemos colocar o paramtero tuple vazio como default?
    response = modelRequest.requestModel(model,prompt,'')

    with open(f'data/guidelines/LLM-generated_guideline_{dataset}.txt', 'w', encoding="utf-8") as resultGuideline:
        resultGuideline.write(response['choices'][0]['message']['content'])
    resultGuideline.close()


def saveLLMgeneratedGuidelines(dataset, guidelineFilepath, fewShotFilepath, msgRequestFilepath):

    # Read all parts of the guideline

    with open(guidelineFilepath, 'r', encoding="utf-8") as mainGuidelineFile:
        mainGuideline = mainGuidelineFile.read()
    mainGuidelineFile.close()
    
    with open(fewShotFilepath, 'r', encoding="utf-8") as fewShotExamplesFile:
        fewShotExamples = fewShotExamplesFile.read()
    fewShotExamplesFile.close()
    
    with open(msgRequestFilepath, 'r', encoding="utf-8") as msgRequestFile:
        msgRequest = msgRequestFile.read()
    msgRequestFile.close()

    # Create the final guideline files

    with open(f'guidelines/LLM-generated_fewshot_{dataset}.txt', 'w', encoding="utf-8") as finalGuidelineFile:
        finalGuidelineFile.write(mainGuideline + '\n' + '\n')
        finalGuidelineFile.write(fewShotExamples + '\n' + '\n')
        finalGuidelineFile.write(msgRequest)
    finalGuidelineFile.close()

    with open(f'guidelines/LLM-generated_zeroshot_{dataset}.txt', 'w', encoding="utf-8") as finalGuidelineFile:
        finalGuidelineFile.write(mainGuideline + '\n' + '\n')
        finalGuidelineFile.write(msgRequest + '\n' + '\n')
    finalGuidelineFile.close()

# Example of use

import pandas as pd

trainTuples = pd.read_csv('data/datasets/wands/wands_200_train_partial.csv')

generatePrompt(trainTuples, 'WANDS', 'furniture and deco')

generateGuideline('data/prompts_for_guideline_generation/prompt_WANDS.txt', 'gpt-3.5-turbo-16k', 'WANDS')

saveLLMgeneratedGuidelines('WANDS', 'data/guidelines/LLM-generated_guideline_WANDS.txt', 'data/datasets/wands/wands_fewshot_partial.txt', 'data/guidelines/msg_requestingAnnotation.txt')