import os, datetime
import numpy, math
from io import StringIO
from contextlib import redirect_stdout
import openai
from gpt_dialogue import Dialogue
# from question_completion_check import question_completion_check
openai.api_key = os.getenv("OPENAI_API_KEY")

class CodeInterpreter(Dialogue):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call_openai_with_code_interpreter(self, user_prompt):
        # call openai with potential code interpreter
        # user_prompt += '\nStop whenever you feel there is need to generate python code (for example, when there is need to do quantitative evaluation) and wait for the result from the code execution.'
        # user_message = [{"role": "user", "content": user_prompt}]
        # completion = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=self.pretext + user_message,
        #     temperature=self.temperature,
        #     top_p=self.top_p,
        #     max_tokens=self.max_tokens,
        # )
        assistant_response = self.call_openai(user_prompt)

        # check if response contain code snippet
        response_content = assistant_response['content']
        # if self.debug:
        #     print('response_content: ', response_content)
        response_splits = response_content.split('```python')
        if len(response_splits) <= 1:
            # no code snippet found, return the raw response
            # if self.debug:
            #     print('no code snippet found, return the raw response')
            return assistant_response
        
        # elif len(response_splits) % 2 == 0:
        #     warning_msg = 'Irregular structued code returned, there should be an even number of code brackets (```)'
        #     print(warning_msg)
        #     return self.call_openai_with_code_interpreter(warning_msg)
        
        else:
            # code snippet found, execute the code
            code_snippet = response_splits[-1].split('```')[0]
            # code_snippet = response_splits[-2]
            # if self.debug:
            #     print('code snippet: ', code_snippet)
            print('code snippet: ', code_snippet)
            # code_exe_result = exec(code_snippet)
            # exec(code_snippet)
            f = StringIO()
            with redirect_stdout(f):
                exec(code_snippet)
            code_exe_result = f.getvalue()
            # if self.debug:
                # print('code execution result: ', code_exe_result)
            print('code execution result: ', code_exe_result)
            code_exe_msg = 'Execution result of the above code is: ' + str(code_exe_result)
            return self.call_openai_with_code_interpreter(code_exe_msg)
        
if __name__ == '__main__':

    config = {
        'model': 'gpt-4',
        # 'model': 'gpt-3.5-turbo',
        'temperature': 0,
        'top_p': 0.0,
        'max_tokens': 'inf',
        'system_message': 'Imagine you are an artificial intelligence assitant with a python interpreter. So when answering questions, you can choose to generate python code (for example, when there is need to do quantitative evaluation) and wait for the result from the code execution. The generated code should always print out the result. The code should be written in python and should be able to run in the python environment with the following packages installed: numpy, math',
        'load_path': 'chats/scene0536_01.json',
        'save_path': 'chats',
        'debug': False
    }

    # dialogue = Dialogue(**config)
    dialogue = CodeInterpreter(**config)
    print('======================Instructions======================')
    print('Type "exit" to exit the dialogue')
    print('Type "reset" to reset the dialogue')
    print('Type "pretext" to see the current dialogue history')
    print('Type "config" to see the current config')
    print('Type "save" to save the current dialogue history')
    print('====GPT Dialogue Initialized, start asking your questions====')

    while True:
        user_prompt = input('You: ')
        if user_prompt == 'exit':
            break
        elif user_prompt == 'reset':
            # dialogue = Dialogue(**config)
            dialogue = CodeInterpreter(**config)
            print('====GPT Dialogue Initialized, start asking your questions====')
            continue
        elif user_prompt == 'pretext':
            print('===Pretext===')
            for message in dialogue.get_pretext():
                print(message)
            print('===Pretext===')
            continue
        elif user_prompt == 'config':
            print('===Config===')
            print(config)
            print('===Config===')
            continue
        elif user_prompt == 'save':
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            dialogue.save_pretext(config['save_path'], timestamp)
            print('Pretext saved to', os.path.join(
                config['save_path'], 'dialogue_' + timestamp + '.json'))
            continue
        else:
            # response = dialogue.call_openai(user_prompt)['content']
            response = dialogue.call_openai_with_code_interpreter(user_prompt)['content']
            print('Bot:', response)
            counter = 0
            # while not question_completion_check(user_prompt, response):
            while not response.endswith('Now the answer is complete.') and counter < 10:
                response = dialogue.call_openai_with_code_interpreter('')['content']
                print('Bot:', response)
                counter += 1
