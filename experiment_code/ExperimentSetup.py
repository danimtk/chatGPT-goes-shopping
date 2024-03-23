import concurrent.futures
import time
from tqdm import tqdm
import logging
import os
import experiment_code.ExperimentDao as ed
import openai
import experiment_code.OpenAIRequest as oair
import random

class ExperimentSetup:

    my_logger = logging.getLogger('experiment_setup')
    my_handler = logging.StreamHandler()
    my_logger.addHandler(my_handler)
    my_logger.setLevel(logging.INFO)


    def __init__(self, conf, mode, llm):
        self.openairequest = oair.OpenAIRequest()
        self.conf = conf
        self.mode = mode
        self.llm = llm

      
    def run(self):

        self.create_directories(os.getcwd(), ['data', 'output'] + self.conf.getTags(self.mode))

        guideline_template = self.conf.getGuidelines(self.mode)

        table = self.conf.getTableName(self.mode)

        edao = ed.ExperimentDao(self.llm)

        lines = edao.selectInstance(table, ['uniqueID', 'query', 'name', 'status'])

        output_file_path = os.path.join(*[self.conf.getOutputPath(self.mode), self.conf.getOutputFilename(self.mode)])

        if os.path.exists(output_file_path):
            fileMode = 'a'
        else:
            fileMode = 'w'

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:     
            for lineInfo, response in tqdm(executor.map(lambda line: self.prepareRequest(self.llm, [guideline_template, line]), lines), total=len(lines)):
                    
                edao.updateInstance(table, lineInfo['uniqueID'], response['content'], response['finish_reason'], response['prompt_tokens'], response['completion_tokens'], response['total_tokens'], response['elapsed_time'])

        edao.closeConnection()


    # define a retry decorator
    def retry_with_exponential_backoff(
        func,
        initial_delay: float = 1,
        exponential_base: float = 2,
        jitter: bool = True,
        max_retries: int = 9,
        errors: tuple = (openai.error.OpenAIError,),
    ):
        """Retry a function with exponential backoff."""
    
        def wrapper(*args, **kwargs):

            num_retries = 0
            delay = initial_delay
    
            # Loop until a successful response or max_retries is hit or an exception is raised
            while True:
                try:
                    return func(*args, **kwargs)
    
                # Retry on specific errors
                except errors as e:

                    num_retries += 1
    
                    # Check if max retries has been reached
                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        )
    
                    # Increment the delay
                    delay *= exponential_base * (1 + jitter * random.random())
    
                    # Sleep for the delay
                    print(f"{delay=} {num_retries=}")
                    time.sleep(delay)
    
                except Exception as e:
                    raise e
    
        return wrapper
    


    #@backoff.on_exception(backoff.expo, (openai.error.APIConnectionError,  openai.error.RateLimitError, openai.error.Timeout, openai.error.ServiceUnavailableError), logger=my_logger)
    @retry_with_exponential_backoff
    def prepareRequest(self, llm, line):

        prompt = line[0] # prompt
        query =  line[1]['query']
        product = line[1]['name']

        tupl = "('{}', '{})\n".format(query, product)

        start_time = time.time()

        response = self.openairequest.requestModel(llm, prompt, tupl)
        
        end_time = time.time()
        elapsed_time = end_time - start_time


        formated_response = {}
        
        formated_response['prompt_tokens']     = response['usage']['prompt_tokens']
        formated_response['completion_tokens'] = response['usage']['completion_tokens']
        formated_response['total_tokens']      = response['usage']['total_tokens']
        formated_response['finish_reason']     = response['choices'][0]['finish_reason']
        formated_response['content']           = response['choices'][0]['message']['content']
        formated_response['elapsed_time']      = elapsed_time
        
        return line[1], formated_response


    def create_directories(self, base_path, directory_names):

        if not directory_names:
            return

        current_directory = os.path.join(base_path, directory_names[0])

        if not os.path.exists(current_directory):
            os.mkdir(current_directory)

        # Recursively create the remaining directories
        self.create_directories(current_directory, directory_names[1:])