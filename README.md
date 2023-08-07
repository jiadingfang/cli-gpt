# Command Line GPT with Interactive Code Interpreter.
Simple conversational command line GPT that you can run locally with OpenAI API to avoid web usage constraints.
## Update 08/07/23
Add **interactive** code interpreter similar to the web version GPT-4 with Code Interpreter from OpenAI that goes back-and-forth between code generation and GPT reasoning. This is different from [LangChain Python Agent](https://python.langchain.com/docs/integrations/toolkits/python) or [codeinterpreter-api](https://github.com/shroominic/codeinterpreter-api.git) that only generate code one shot. Only focus on python interpreter with numeric usages for now. There are some examples in the `examples` folder.
## Usage
Export `OPENAI_API_KEY` and run `python gpt_dialogue.py` or `python code_interpreter.py`. There are special commands like "save", "pretext", "reset" in the conversation that you can use for convenience. 


