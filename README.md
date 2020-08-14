# dictionary-kanji-bot
a Reddit bot in Python 3.6 that enables lookup of Japanese words or random Kanji. Users can summon the bot using particular strings, also indicating 
whether they require a random kanji and its associated definitions or to look up a certain kanji, kana, or romaji term. The bot uses PRAW
and the jisho.org API.

## Instructions to Run
this program requires a config.py file in the same directory as the main script file and in the following format:

username = "..."

password = "..."

client_id = "..."

client_secret = "..."