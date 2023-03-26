import os
import json
import openai
from time import time, sleep
from flask import Flask, render_template, request
from dotenv import load_dotenv
from difflib import SequenceMatcher

app = Flask(__name__)
load_dotenv()

def load_training_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)["faq"]
    return data

training_data = load_training_data("faq.json")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def search_training_data(userText, training_data, threshold=0.8):
    for entry in training_data:
        if similar(userText, entry['question']) > threshold:
            return entry['answer']
    return None

def bot(prompt, training_data, engine='text-davinci-002', temp=0.9, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.5, stop=['<<END>>']):
    # Rest of the code remains the same
    max_retry = 1
    retry = 0
    api_key = os.getenv('api_key')  # Get API key from .env file
    openai.api_key = api_key
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=[" User:", " AI:"])
            text = response['choices'][0]['text'].strip()
            print(text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
               outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response_from_data = search_training_data(userText, training_data)
    
    if response_from_data:
        return response_from_data
    else:
        botresponse = bot(prompt=userText, training_data=training_data)
        return str(botresponse)

if __name__ == "__main__":
    app.run(debug=True)
