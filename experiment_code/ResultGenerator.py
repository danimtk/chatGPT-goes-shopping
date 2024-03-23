import pandas as pd
import numpy as np
import os
import re
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import cohen_kappa_score
import experiment_code.ExperimentDao as exp

class ResultGenerator:

    def __init__(self):
        pass

    def parsingDatabase(self, conf, mode, llm):

        edao = exp.ExperimentDao(llm)

        regex_not_relevant = re.compile(r'Not relevant', re.IGNORECASE)

        regex_relevant = re.compile(r'Relevant', re.IGNORECASE)


        output_formated_judgment_file_path = os.path.join(*[conf.getOutputPath(mode), conf.getOutputFormatedJudgmentFilename(mode)])


        rows = edao.selectJudgedInstances(conf.getTableName(mode), ['content', 'elapsed_time', 'prompt_tokens', 'completion_tokens', 'target'])

        df_db = pd.DataFrame(rows)

        df_db['truth'] = ""
        df_db['predicted_target'] = ""

        new_column_names = {'prompt_tokens': 'input', 'completion_tokens': 'output', 'content' : 'response', 'label' : 'target'}
        df_db.rename(columns=new_column_names, inplace=True)

        for idx, line in df_db.iterrows():

                judgment = None
                    
                if regex_not_relevant.search(line.at['response']):

                    judgment = 'Not Relevant'

                elif regex_relevant.search(line.at['response']):

                    judgment = 'Relevant'
                
                else:

                    print('Unexpected judgment label for the following tuple: ', line)

                df_db.loc[idx, 'truth'] = df_db.loc[idx, 'target'] 
                df_db.loc[idx, 'predicted_target'] = judgment


        del df_db['target'] 

        df_db.to_csv(output_formated_judgment_file_path, index=False)


    def saveMetrics(self, conf, llm):

        runs = conf.getRuns()

        df_results = pd.DataFrame(columns=['run', 'acc', 'f1', 'kappa', 'precision', 'recall', 'TP', 'TN', 'FP', 'FN'])

        for run in runs:

            path = conf.getOutputPath(run)
            filename = conf.getOutputFormatedJudgmentFilename(run)

            output_file_path = os.path.join(*[path, filename])

            if os.path.exists(output_file_path):

                df = pd.read_csv(output_file_path, sep=',')

                df = df[~df['predicted_target'].isna()]

                y_true = df['truth'].str.lower()
                y_pred = df['predicted_target'].str.lower()

                # metrics
                acc = accuracy_score(y_true, y_pred, normalize=True)

                f1 = f1_score(y_true, y_pred, pos_label='relevant', average='binary', zero_division=np.nan)

                kappa = cohen_kappa_score(y_true, y_pred)
                
                pre = precision_score(y_true, y_pred, pos_label='relevant', average='binary', zero_division=np.nan)

                rec = recall_score(y_true, y_pred, pos_label='relevant', average='binary', zero_division=np.nan)

                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()


                new_entry = pd.DataFrame([[run, acc, f1, kappa, pre, rec, tp, tn, fp, fn]], columns=['run', 'acc', 'f1', 'kappa', 'precision', 'recall', 'TP', 'TN', 'FP', 'FN'])

                df_results = pd.concat([df_results, new_entry], ignore_index=True)
                
        df_results.to_csv(f"data/output/summary_results_{llm}.csv", index=False)

"""
if __name__ == "__main__":

    confPath = 'conf//conf_gpt35.json'

    confSetup = cs.ConfSetup(confPath)

    resGen = ResultGenerator()

    resGen.parsingDatabase(confSetup, 'wands_ten_shot_LLM_generated', 'gpt-3.5-turbo')

    resGen.saveMetrics(confSetup, 'gpt-3.5-turbo')

"""
