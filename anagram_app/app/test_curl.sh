!#/bin/bash


curl -i -X POST -H "Content-Type: application/json" -d '{ "words": [ "thewordwitchnotexists"] }' http://localhost:8080/words.json

curl -i -X DELETE  http://localhost:8080/words/thewordwitchnotexists.json

curl -i -X GET  http://localhost:8080/anagrams/thewordwitchnotexists.json

curl -i -X GET  'http://localhost:8080/anagrams/bar.json?limit=2'

curl -i -X DELETE  http://localhost:8080/words.json

curl -i -X GET  http://localhost:8080/reinitdb.json

curl -i -X GET  http://localhost:8080//stats/most_anagrams.json

curl -i -X GET  'http://localhost:8080//stats/anagrams_word_size.json?size=5'

curl -i -X POST -H "Content-Type: application/json" -d '{ "words": [ "bar","bra"] }' http://localhost:8080/isanagrams.json