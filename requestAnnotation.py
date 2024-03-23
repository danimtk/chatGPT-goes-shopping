import argparse
import experiment_code.ExperimentSetup as exp
import experiment_code.ConfSetup as cs

mode_mapping = {'fewshot_human'            : 'wands_ten_shot_human_baseline',
                'fewshot_llm'              : 'wands_ten_shot_LLM_generated',
                'zeroshot_human'           : 'wands_zero_shot_human_baseline',
                'zeroshot_llm'             : 'wands_zero_shot_LLM_generated',
                'fewshot_withoutguideline' : 'wands_ten_shot_without_guideline'
            }
    
llm_mapping = {'gpt35' : {
                            'model' : 'gpt-3.5-turbo', 
                            'conf'  : 'conf/conf_gpt35.json'},
                'gpt4' : {
                            'model' : 'gpt4', 
                            'conf'  : 'conf/conf_gpt4.json'}
            }

parser = argparse.ArgumentParser(description='')

parser.add_argument('--mode',
                    required=True,
                    choices=['fewshot_human', 'fewshot_llm', 'zeroshot_human', 'zeroshot_llm', 'fewshot_withoutguideline'], 
                    help='Description of mode argument. There are four available modes: \n fewshot_human \n fewshot_llm \n zeroshot_human \n zeroshot_llm \n fewshot_withoutguideline'
                )

parser.add_argument('--llm', 
                    default='gpt35',
                    choices=['gpt35', 'gpt4'],
                    help='Description of Large Language Model (LLM) argument. There are two available llm: \n gpt35 \n gpt4 '
                )

try:

    args = parser.parse_args()

    mode_param = args.mode

    mode = mode_mapping[mode_param]
    llm = llm_mapping[args.llm]['model']
    conf = llm_mapping[args.llm]['conf']

    confSetup = cs.ConfSetup(conf)


    print(f'Running {mode_param} on {llm}...')

    experiment = exp.ExperimentSetup(confSetup, mode, llm)
    experiment.run()

except argparse.ArgumentError:
    
    print("Required argument(s) not provided. Please specify 'mode' and 'llm' arguments.")


except KeyboardInterrupt as e:

    print(f'Execution interrupted')