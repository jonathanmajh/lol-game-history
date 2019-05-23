import requests
import math
import json
import time
import sys
import sqlite3
def get_matches(api_key,  str_in,  encrypt_a):
    r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?api_key={}&endIndex=20000&beginIndex=19900'.format(encrypt_a,  api_key))
    r = r.json()
    text_file = open('{}_match_history.txt'.format(str_in),  'w')
    matches = []
    if r['totalGames'] == 0:
        print('No Games Played')
        sys.exit()
    else:
        total_games = r['totalGames'] 
        print(total_games/100)
        print(math.ceil(total_games/100))
        hits = math.ceil(total_games/100)
        for hit in range(hits):
            r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?api_key={}&endIndex={}&beginIndex={}'.format(encrypt_a,  api_key,  (hit+1)*100,  hit*100))
            if r.status_code != requests.codes.ok:
                str_in = input("POST returned code: {} ".format(r.status_code));
                sys.exit()
            r = r.json()
            text_file.write('Matches {} - {}\n'.format(hit*100,  (hit+1)*100))
            text_file.write(json.dumps(r, indent=4)) # write json results to text file
            text_file.write('\n') # new line just in case
            print('Processing matches {} - {}'.format(r['startIndex'],  r['endIndex']))
            for match in r['matches']:
                matches.append(match['gameId'])
            time.sleep(1)
    text_file.close()
    matches_file = open('{}_matches.txt'.format(str_in),  'w')
    for match in matches:
        matches_file.write(str(match))
        matches_file.write('\n')
    matches_file.close()
    return matches

def process_matches(str_in,  matches,  api_key,  db):
    cursor = db.cursor()
    matches_detailed_file = open('{}_matches_detail.txt'.format(str_in),  'w')
    total_time = 0
    i = 0
    for match in matches:
        i = i + 1
        print('Processing Match: {}'.format(i))
        cursor.execute('''SELECT id, duration FROM games_detailed WHERE id=?''', (match,))
        sql_match = cursor.fetchone()
        if sql_match is None:
            r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/{}?api_key={}'.format(str(match),  api_key))
            if r.status_code != requests.codes.ok:
                str_in = input("POST returned code: {} ".format(r.status_code));
                sys.exit()
            r = r.json()
            cursor.execute('''insert into games_detailed(id, duration, game_detail)values(?,?,?)''',  (match,  r['gameDuration'],  json.dumps(r, indent=4)))
            db.commit()
            matches_detailed_file.write(json.dumps(r, indent=4))
            matches_detailed_file.write('\n') 
            total_time = total_time + r['gameDuration']
            time.sleep(2)
        else:
            total_time = total_time + sql_match[1]
        print('Total Time so Far: {} minutes'.format(total_time/60))
    print('Total Time so Far: {} hours'.format(total_time/3600))
    matches_detailed_file.close()
    
def main():
    db = sqlite3.connect('data/mydb')
    api_key = '[API_KEY]'
    str_in = input("Enter Summoner Name ");
    r = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}'.format(str_in,  api_key))
    encrypt_a = r.json()['accountId']
    print('the encrypted user id is: {}'.format(encrypt_a))
    # initial match list hit, we use this to get the minimum number of games
    matches = get_matches(api_key,  str_in,  encrypt_a)
    process_matches(str_in,  matches,  api_key,  db)
    
main()
