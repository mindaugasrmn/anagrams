from fastapi import FastAPI, status, Request, HTTPException
import uvicorn
import redis
from typing import Any, Dict, AnyStr, List, Union
from pydantic import BaseModel
import asyncio
import copy

r = redis.Redis(host='redis_db', port=6379, decode_responses=True)

class Words(BaseModel):
    words: List


def get_key(word: str):
    word=sorted(word.strip().lower())
    return ''.join(str(x) for x in word)

def check_if_words_is_anagrams(words:[]):
    anagram=True
    key=get_key(words[0])
    words.pop(0)
    for word in words:
        if key!=get_key(word):
            anagram=False
    return anagram

app = FastAPI()
def init_db():

    file1 = open('/app/app/dictionary.txt', 'r')
    Lines = file1.readlines()
    
    #from wikipedia: An anagram is a word or phrase formed by rearranging the letters of a different word or phrase, 
    #typically using all the original letters exactly once.
    #so iterrating every line and formatting dictionary as folowing
    # anagrams of car:
    # key: acr, value: ['car','arc',...]
    for line in Lines:
        key=get_key(line)
        r.lpush(key, line.strip())

    

#initializing dictionary as global variable
#init_db()

#get all anagrams
@app.post('/isanagrams.json')
async def is_anagrams(words: Request):
    req=await words.json()
    return {'words_is_anagrams':check_if_words_is_anagrams(req['words'])}


#get anagrams of word, limit output if not set return 10 anagrams, exclude nouns (default false)
@app.get('/anagrams/{word}.json')
async def get_anagram(word: str, limit: int = 10, noun: bool = False):
    key=get_key(word)
    anagrams=r.lrange(key,0,-1)
    if len(anagrams)>0:

        #remove word wich was requested
        if word in anagrams:
            anagrams.remove(word)

        #if limit set return only limited anagrams
        if limit:
            anagrams = anagrams[:limit]

        #noun stuff, it is not wery correct wat to do it, I will consider using ntlk to identify nouns
        if noun and anagrams and word[0].isupper():
            anagrams = [item for item in anagrams if word[0] == item[0]]
        return {'anagrams': anagrams}
    else:
        #not found haldner
        return HTTPException(status_code=404, detail="Anagram not found in db")

#create anagram record
@app.post('/words.json',status_code=201)
async def create_anagrams(words: Request):
    req=await words.json()
    ifExists=r.keys(get_key(req['words'][0]))
    if len(ifExists)==0:    
        key=get_key(req['words'][0])
        for word in req['words']:
            r.lpush(key, word.strip())
        return status.HTTP_201_CREATED
    return HTTPException(status_code=500, detail="Anagram already exists")


#delete anagrams by word    
@app.delete('/words/{word}.json')
async def delete_anagram(word: str):
    key=get_key(word)
    res=r.delete(key)
    if res==1:
        return status.HTTP_200_OK
    return status.HTTP_404_NOT_FOUND


#finds word which have most anagrams
@app.get('/stats/most_anagrams.json')
async def get_stats_most_anagrams():
    most_anagrams=""
    keys=r.keys()
    most_anagrams_count=0
    for key in keys:
        key_len=r.llen(key)
        if most_anagrams_count<key_len:
            most_anagrams_count=key_len
            most_anagrams=key
    anagrams=r.lrange(most_anagrams,0,-1)

    return {'anagrams': anagrams, 'total_anagrams':len(keys), 'most_anagrams_count':most_anagrams_count}

#finds anagrams groups by word length
@app.get('/stats/anagrams_word_size.json')
async def get_stats_most_anagrams(size:int):
    keys=r.keys()
    anagrams=[]
    for key in keys:
        if len(key)==size:
            anagrams.append(copy.copy(r.lrange(key,0,-1)))


    return {'anagrams_groups': anagrams, 'total_groups':len(anagrams)}


    
@app.delete('/words.json')
async def delete_anagrams():
    r.execute_command("flushall")
    return status.HTTP_200_OK


@app.get('/reinitdb.json')
async def get_anagrams():
    r.execute_command("flushall")
    init_db()
    return status.HTTP_200_OK

# serving app with uvicorn
# store data in array not a good idea as if uvicorn will run more then one worker, each worker will have separate data
# so we will use redis

# if __name__ == "__main__":
#    uvicorn.run("main:app", host='localhost', port=8000, log_level="info")