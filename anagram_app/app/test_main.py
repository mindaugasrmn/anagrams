from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)

def test_add_words():

    # create new anagram
    words=['testword','wordtest']
    response = client.post('/words.json', json={'words': words})
    print(response.status_code)
    assert response.status_code == 201
    


def test_delete_word():
    
    word = 'testword'

    # delete testword to db
    response = client.delete(f'/words/{word}.json')
    assert response.status_code == 200



def test_delete_all():

    #remove alld words
    response = client.delete('/words.json')
    assert response.status_code == 200

    #reinit db for future tests
    response = client.get('/reinitdb.json')
    assert response.status_code == 200
    


def test_get_anagrams():
   

    # testing a default case
    words=['testword','wordtest']
    _ = client.post('/words.json', json={'words': words})
    word = 'testword'
    response = client.get(f'/anagrams/{word}.json')
    anagrams_ok = ['testword', 'wordtest']
    assert response.status_code == 200
    #assert all(anagram in response.json()['anagrams'] for anagram in anagrams_true)

    # testing a noun case
    word = 'testword'
    _ = client.delete(f'/words/{word}.json')
    word = 'Testword'
    anagrams_ok = ['Testword', 'Wordtest',"TestWord"]
    _ = client.post('/words.json', json={'words': anagrams_ok})
    response = client.get(f'/anagrams/{word}.json?noun=true')
    assert response.status_code == 200
    #assert all(anagram in response.json()['anagrams'] for anagram in anagrams_true)

    # testing limit
    word = 'bar'
    response = client.get(f'/anagrams/{word}.json?limit=2')
    print(response.status_code)
    assert response.status_code == 200
    assert len(response.json()['anagrams']) == 2


def test_is_anagrams():


    # positive case
    words = ['rab','Rab', 'bra','bar']
    response = client.post('/isanagrams.json', json={'words': words})
    print(response.status_code)
    assert response.status_code == 200
    assert response.json()

    # negative case
    words = ['rab','Rab', 'bra','bar', 'AAA']
    response = client.post('/isanagrams.json', json={'words': words})
    print(response.status_code)
    assert response.status_code == 200
    assert response.json()


