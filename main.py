from flask import Flask
import pyodbc, random


server = 'vorbededuh.database.windows.net'
database = 'vorbededuh'
username = 'tudork'
password = 'Cl0udComputing'
driver= '{ODBC Driver 13 for SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()





app = Flask(__name__)

@app.route('/')
def random_quote():

  cursor.execute(
    "SELECT author, quote FROM Quotes WHERE id='"+random.randint(1, 36165)+"'")
  row = cursor.fetchone()
  return row

if __name__ == '__main__':
  app.run()
