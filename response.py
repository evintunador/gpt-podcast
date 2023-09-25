import openai
from time import time, sleep
import textwrap
import yaml
from config import API_KEY, model, context


###     file operations
def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)

def open_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


###     API functions
def chatbot(conversation, model=model, temperature=0):
    max_retry = 3
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature)
            text = response['choices'][0]['message']['content']
            
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            if 'maximum context length' in str(oops):
                a = conversation.pop(0)
                print('\n\n DEBUG: Trimming oldest message')
                continue
            retry += 1
            if retry >= max_retry:
                print(f"\n\nExiting due to excessive errors in API: {oops}")
                exit(1)
            print(f'\n\nRetrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)


def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nCHATBOT:\n\n%s' % formatted_text)


context_len_dict = {'gpt-3.5-turbo-16k': 44000,
                  'gpt-4-32k': 88000,
                  'gpt-4': 22000,
                  'gpt-3.5-turbo': 11000}
context_len = context_len_dict[model]

max_tokens = {'gpt-3.5-turbo-16k': 15900,
                  'gpt-4-32k': 31600,
                  'gpt-4': 7800,
                  'gpt-3.5-turbo': 3800}


if __name__ == '__main__':
    # no point in calling if there's no API key
    if API_KEY == '':
        print("API key not found in config.py. Exiting.")
        exit(1)
    openai.api_key = API_KEY

    if len(context) > context_len:
        context = context[0:context_len]
    ALL_MESSAGES = [{'role':'system', 'content': context}]
    while True:
        # get user input
        text = input('\n\n\nUSER:\n\n')
        if text == '':
            # empty submission, probably on accident
            continue
        ALL_MESSAGES.append({'role': 'user', 'content': text})
        
        # get response
        response, tokens = chatbot(ALL_MESSAGES)
        if tokens >= max_tokens[model]:
            a = ALL_MESSAGES.pop(1)
        chat_print(response)
        ALL_MESSAGES.append({'role': 'assistant', 'content': response})
