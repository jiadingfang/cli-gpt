import os
from huggingface_hub import login

hf_token = os.getenv("HUGGINGFACE_TOKEN")
login(token=hf_token)
os.environ['TRANSFORMERS_CACHE'] = '/share/data/2pals/fjd/.cache/huggingface'

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, Conversation

def setup_pipeline(model_name, temperature=1e-7, top_p=1e-7, max_length=512):
    # set up resources
    # free_in_GB = int(torch.cuda.mem_get_info()[0]/1024**3)
    max_memory = f'{int(torch.cuda.mem_get_info()[0]/1024**3)-2}GB'
    n_gpus = torch.cuda.device_count()
    max_memory = {i: max_memory for i in range(n_gpus)}

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map='auto',
        load_in_4bit=True,
        # load_in_8bit=True,
        # torch_dtype=torch.bfloat16, 
        use_flash_attention_2=True,
        max_memory=max_memory
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    conversational_pipeline = pipeline(
        "conversational",
        model=model,
        tokenizer=tokenizer,
        do_sample=True,
        temperature=temperature+1e-7,
        top_p=top_p+1e-7,
        max_length=max_length,
    )

    return model, tokenizer, conversational_pipeline

class HuggingfaceConversational:
    def __init__(self, model_name, temperature=1e-7, top_p=1e-7, max_length=512):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_length = max_length
        self.model, self.tokenizer, self.conversational_pipeline = setup_pipeline(model_name, temperature, top_p, max_length)

    def __call__(self, conversation):
        return self.conversational_pipeline(conversation)
        

if __name__=="__main__":
    # check out https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L212 to see what's the best format for llama2 chat model
    model_name = 'meta-llama/Llama-2-7b-chat-hf'
    # model_name = 'meta-llama/Llama-2-7b-hf'
    # model_name = 'meta-llama/Llama-2-13b-chat-hf'
    # model_name = 'meta-llama/Llama-2-13b-hf'
    # model_name = 'meta-llama/Llama-2-70b-chat-hf'
    # model_name = 'codellama/CodeLlama-34b-Instruct-hf' # not ready yet
    # model_name = 'codellama/CodeLlama-13b-Python-hf' # not ready yet
    # model_name = 'codellama/CodeLlama-34b-Python-hf' # not ready yet
    # model_name = 'mistralai/Mistral-7B-Instruct-v0.1' # not ready yet, look at https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
    # model_name = 'mistralai/Mistral-7B-v0.1' # not ready yet, look at https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
    model = HuggingfaceConversational(model_name)
    # print(model('What is the captial of France?'))
    # print(model('hi how are you?'))
    conversation_1 = Conversation("Going to the movies tonight - any suggestions?")
    # conversation_2 = Conversation("What's the last book you have read?")
    answer = model(conversation_1)
    print(answer.messages)

