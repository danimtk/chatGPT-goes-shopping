import os
import openai

class OpenAIRequest:

    def __init__(self):

        self.count = 0

        self.api_key =  os.environ.get('OPENAI_KEY')

        if self.api_key is None:
            raise ValueError("Environment variable OPENAI_KEY is not set.")

        openai.api_key = self.api_key


        self.params = {
            'temperature': 0,
            'max_tokens': None,
            'n' : 1,
            'top_p' : 1,
            'stop' : None,
            'presence_penalty': 0,
            'frequency_penalty': 0
        }
        

    def requestModel(self, llm, prompt, tupl):

        messages = [{"role" : "system", "content" : prompt}, {"role" : "user", "content" : tupl}]

        response = openai.ChatCompletion.create(
            model = llm,
            messages = messages,
            temperature = self.params['temperature'],
            max_tokens = self.params['max_tokens'],
            n = self.params['n'],
            stop = self.params['stop'],
            presence_penalty = self.params['presence_penalty'],
            frequency_penalty = self.params['frequency_penalty']
        )

        return response