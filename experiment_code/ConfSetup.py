import os
import json

'''
    Script used to read the configuration file
'''

def jsonReader(file_path):

    data = None

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    return data

class ConfSetup:

    def __init__(self, conf_path):

        self.data = jsonReader(conf_path)

    def getRuns(self):
        
        return list(self.data.keys())

    def getOutputPath(self, mode):

        return os.path.join('data', 'output', *self.data[mode]['tags'])

    def getOutputFilename(self, mode):

        return self.data[mode]['output_judgment']

    def getOutputFormatedJudgmentFilename(self, mode):

        return self.data[mode]['output_judgment_file_formatted']
    
    def getTableName(self, mode):
        return self.data[mode]['table']
    
    def getGuidelines(self, mode):
        guidelines = None

        filename =  self.data[mode]['input_guideline_template']

        with open(filename, "r") as outfile:
            guidelines = outfile.read()

        return guidelines
    
    def getTags(self, mode):
        return self.data[mode]['tags']