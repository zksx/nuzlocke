# code that gets the data from pokemondb.net and then gets rid of duplicates
# from mega evloves. Give us the pokemon database "pokemon.db"

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


url = "https://pokemondb.net/pokedex/all"
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

table = soup.find('table', class_='data-table sticky-header block-wide')

A = []
B = []
C = []
D = []
E = []
F = []
G = []
H = []
I = []
J = []

for row in table.findAll("tr"):
    states = row.findAll('th')
    cells = row.findAll('td')
    if len(cells) == 10:
        A.append(cells[0].find(string=True))
        B.append(cells[1].find(string=True))
        C.append(cells[2].find(string=True))
        D.append(cells[3].find(string=True))
        E.append(cells[4].find(string=True))
        F.append(cells[5].find(string=True))
        G.append(cells[6].find(string=True))
        H.append(cells[7].find(string=True))
        I.append(cells[8].find(string=True))
        J.append(cells[9].find(string=True))
        
df = pd.DataFrame(A, columns=['#'])

df['Name'] = B
df['Type'] = C
df['Total'] = D
df['HP'] = E
df['Attack'] = F
df['Defense'] = G
df['Special Attack'] = H
df['Special Defense'] = I
df['Speed'] = J

conn = sqlite3.connect('{}.db'.format("nuzlocke")) # creates file
df.to_sql("pokemon", conn, if_exists='replace', index=False) # writes to file

cursor = conn.cursor()

# Statement excludes mega evolutions
cursor.execute("DELETE FROM pokemon WHERE EXISTS \
               (SELECT 1 FROM pokemon p WHERE p.Name = pokemon.Name \
               AND p.rowid < pokemon.rowid);")
conn.commit()

conn.close() # good practice: close connection
