import os
import json
import datetime
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")


class Dialogue:
    def __init__(self, model='gpt-4', temperature='0', max_tokens='10', system_message='', load_path=None, save_path='chats'):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = system_message
        self.save_path = save_path
        if load_path is not None:
            self.load_pretext(load_path)
        else:
            self.pretext = [{"role": "system", "content": self.system_message}]

    def load_pretext(self, load_path):
        
        def load_json(load_path):
            with open(load_path) as json_file:
                return json.load(json_file)
            
        self.pretext = []
        if isinstance(load_path, list):
            for path in load_path:
                self.pretext += load_json(path)
        elif isinstance(load_path, str):
            self.pretext = load_json(load_path)
        else:
            raise Exception('load_path must be a list of strings or a string')

    def get_pretext(self):
        return self.pretext

    def save_pretext(self, save_path, timestamp):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        json_path = os.path.join(save_path, 'dialogue_' + timestamp + '.json')
        json_object = json.dumps(self.get_pretext(), indent=4)
        with open(json_path, 'w') as f:
            f.write(json_object)

    def call_openai(self, user_prompt):
        user_message = [{"role": "user", "content": user_prompt}]
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.pretext + user_message,
        )
        assistant_response = completion.choices[0].message
        self.pretext = self.pretext + user_message + [assistant_response]
        return assistant_response


if __name__ == '__main__':

    config = {
        'model': 'gpt-4',
        'temperature': 0,
        'max_tokens': 'inf',
        'system_message': '',
        'load_path': 'chats/zork_70.json',
        'save_path': 'chats',
    }

    dialogue = Dialogue(**config)
    print('===Config===')
    print(config)
    print('===Config===')
    print('Type "exit" to exit the dialogue')
    print('Type "reset" to reset the dialogue')
    print('Type "pretext" to see the current dialogue history')
    print('Type "save" to save the current dialogue history')
    print('====GPT Dialogue Initialized, start asking your questions====')

    while True:
        user_prompt = input('You: ')
        if user_prompt == 'exit':
            break
        elif user_prompt == 'reset':
            dialogue = Dialogue(**config)
            print('====GPT Dialogue Initialized, start asking your questions====')
            continue
        elif user_prompt == 'pretext':
            print('===Pretext===')
            for message in dialogue.get_pretext():
                print(message)
            print('===Pretext===')
            continue
        elif user_prompt == 'save':
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            dialogue.save_pretext(config['save_path'], timestamp)
            print('Pretext saved to', os.path.join(
                config['save_path'], 'dialogue_' + timestamp + '.json'))
            continue
        else:
            response = dialogue.call_openai(user_prompt)['content']
            print('Bot:', response)
