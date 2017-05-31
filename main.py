from flask import Flask, jsonify, render_template
import pyodbc, random, requests, http.client, base64
from xml.etree import ElementTree


server = 'vorbededuh.database.windows.net'
database = 'vorbededuh'
username = 'tudork'
password = 'Cl0udComputing'
driver= '{ODBC Driver 13 for SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

def random_quote():
  cursor.execute("SELECT author, quote FROM Quotes"
                 " WHERE id='"+str(random.randint(1, 36165))+"'")
  row = cursor.fetchone()

  return row[0], row[1]

def get_photo():
  url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'
  headers = {'Ocp-Apim-Subscription-Key' : 'fccd834e8c484449b6bfbba0722eacab'}
  r = requests.get(url, headers= headers, params= {'q': 'landscape'})
  return r.json()

def get_gender(name):
  return requests.get('https://api.genderize.io/?name=' + name).json()


def get_audio(text, gender):
  params = ""
  headers = {"Ocp-Apim-Subscription-Key": '5d902961b17745118bf672cbabfad526'}

  # AccessTokenUri = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken";
  AccessTokenHost = "api.cognitive.microsoft.com"
  path = "/sts/v1.0/issueToken"

  # Connect to server to get the Access Token
  conn = http.client.HTTPSConnection(AccessTokenHost)
  conn.request("POST", path, params, headers)
  response = conn.getresponse()

  data = response.read()
  conn.close()

  accesstoken = data.decode("UTF-8")

  body = ElementTree.Element('speak', version='1.0')
  body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
  voice = ElementTree.SubElement(body, 'voice')
  voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
  if gender == "female":
    voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Female')
    voice.set('name',
            'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)')
  elif gender == "male":
    voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Male')
    voice.set('name',
              'Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)')

  voice.text = text

  headers = {"Content-type": "application/ssml+xml",
             "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
             "Authorization": "Bearer " + accesstoken,
             "X-Search-AppId": "07D3234E49CE426DAA29772419F436CA",
             "X-Search-ClientID": "1ECFAE91408841A480F00935DC390960",
             "User-Agent": "TTSForPython"}

  # Connect to server to synthesize the wave
  conn = http.client.HTTPSConnection("speech.platform.bing.com")
  conn.request("POST", "/synthesize", ElementTree.tostring(body), headers)
  response = conn.getresponse()


  data = response.read()
  conn.close()

  return data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/random')
def get_quote():
  a = get_photo()

  author, quote = random_quote()
  gender = get_gender(author.split(' ')[0])["gender"]
  audio = get_audio(quote, gender)


  audio = base64.b64encode(audio)

  return jsonify({"author": author, "quote": quote, "gender": gender,
                  "image": random.choice(a["value"])["contentUrl"],
                  "audio": audio.decode('utf-8')})



if __name__ == '__main__':
  app.run(debug=True)
