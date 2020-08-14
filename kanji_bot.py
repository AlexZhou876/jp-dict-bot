import json
import os
import random
import time

import praw
import requests

import config

# lower and upper bounds for unicode block containing common CJK characters
UNICODE_LOWER_BOUND = 0x4E00
UNICODE_UPPER_BOUND = 0x9FFF
RANDOM_SUMMONS = ["random chinese character", "random kanji", "random hanzi", "random hanja", 'random 汉字', 'random 漢字']
LOOKUP = '!lookup'

def authenticate():
    """authenticate bot using praw api."""
    r = praw.Reddit(username = config.username,
                    password = config.password,
                    client_id  = config.client_id,
                    client_secret = config.client_secret,
                    user_agent = "kanjibot")
    return r

# main loop
def run_bot(r, comments_replied_to):
    print('runbotstarted')
    for comment in r.subreddit('test').comments(limit=40):
        summon = find_summon(comment.body)
        if summon is not None and comment.id not in comments_replied_to and comment.author != r.user.me(): 
            print("summon detected")
            comment.reply(generate_reply(summon))
            comments_replied_to.add(comment.id)
            with open("comments_replied_to.txt", "a") as f:
                f.write(comment.id + "\n")
    

#old 
'''
def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
        with open("comments_replied_to.txt", "r") as f:
            comments_replied_to = f.read()
            comments_replied_to = comments_replied_to.split("\n")
    return comments_replied_to
'''
def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        return set()
    else:
        with open("comments_replied_to.txt") as f:
            return {line.rstrip() for line in f}
    


# nothing -> str
# return str containing random chinese character in CJK Unified Ideographs Unicode block.
def generate_random_kanji():
    codepoint = random.randint(UNICODE_LOWER_BOUND, UNICODE_UPPER_BOUND)
    return chr(codepoint)

# str -> boolean
# return true if body contains a trigger string
def summoned(body):
    return any(summon in body for summon in RANDOM_SUMMONS)

# str -> str or None
# if summon is !lookup, return query within !lookup flags. Otherwise, if summon is random, return the summon.
def find_summon(body):
    if LOOKUP in body:
        return body.split('!lookup')[1]
    for summon in RANDOM_SUMMONS:
        if summon in body:
            return summon
    return None


def generate_reply(summon):
    """build and return the reply string based on the summon string"""
    reply = ''
    query = ''
    if summon in RANDOM_SUMMONS:
        query = generate_random_kanji()
        reply = '#**You asked for a random Chinese character. Here it is: ' + query + '**'
    else:
        query = summon.replace('!lookup', '')
        reply += '#**You asked to define ' + query + '**'

    reply += '\n# Japanese Definitions:'
    # below is the best practice for get(): pass in queries as a dict literal or name
    # and call raise for status after the call to raise an exception for error codes 4xx, 5xx
    r = requests.get('https://jisho.org/api/v1/search/words', {'keyword' : query})
    r.raise_for_status() 
    # type of definitions_data: list of dict, each dict is a definition
    definitions_data = r.json()['data']
    
    if definitions_data == []:
        reply += ' no Japanese definitions found\n'
    else: 
        for defin in definitions_data:
            try:
                reply += '\n\nWord: ' + defin['slug']
                reply += '\n\nReading: ' + defin['japanese'][0]['reading']
                reply += '\n\nEnglish Definition: ' + defin['senses'][0]['english_definitions'][0]
            except: 
                reply += '\n\nError: Missing information for this definition'
    reply += '\n\nimprovements to come'
    print(reply)
    return reply
    

# main function: so this module can be imported without executing main functionality.
def main():
    reddit = authenticate()
    comments_replied_to = get_saved_comments()
    while True:
        run_bot(reddit, comments_replied_to)

## end definitions
## begin executions
if __name__ == '__main__':
    main()
