import sqlite3
db = sqlite3.connect('data/mydb')
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE games(id INTEGER PRIMARY KEY, gameId UNSIGNED BIG INT,  match_detail text)
''')
cursor.execute('''
    CREATE TABLE games_detailed(id INTEGER PRIMARY KEY, duration integer, game_detail text)
''')
db.commit()
db.close()
