from flask import Flask, render_template, request, jsonify
import requests
from time import ctime
from bs4 import BeautifulSoup
import sqlite3 as lite
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def index():
    naver_uri = "https://www.naver.com/"
    executed_time = ctime()
    naver_html = requests.get(naver_uri).text

    soup = BeautifulSoup(naver_html, 'html.parser')
    kw_ul = soup.find('ul', attrs={'class':'ah_l'})
    keywords = [li.text for li in kw_ul.find_all('span', attrs={'class':'ah_k'})]

    return render_template('index.html', time=executed_time, keywords=keywords)

@app.route('/user/<string:name>')
def user(name=None):
    return render_template('user.html', msg=name)

@app.route('/users')
def users():
    keywords = request.args
    return render_template('users.html', rows=keywords )

@app.route('/movies', methods=["GET","POST"])
def movies():
    if request.method == "GET":
        try:
            conn = lite.connect('./data/data.db')
            conn.row_factory = lite.Row

            cur = conn.cursor()
            query="SELECT * FROM Movies;"
            cur.execute(query)

            rows = cur.fetchall()
            conn.close()

            return render_template('movies.html', rows=rows)
        except:
            pass

    elif request.method == "POST":
        try:
            input_name = request.form["movie-name"]
            input_year = request.form["movie-year"]
            input_studio = request.form["movie-studio"]

            with lite.connect('./data/data.db') as conn:
                cur = conn.cursor()
                query= """
                    INSERT INTO Movies(name,year,studio)
                    VALUES(?,?,?);
                """
                cur.execute(query,(input_name,input_year,input_studio))
                conn.commit()
                msg = "Success"
        except:
            conn.rollback()
            msg = "Failed"
        finally:
            return render_template('movies.html', msg=msg)


mongo_uri = "mongodb://strongadmin:admin1234@ds135844.mlab.com:35844/mydbinstance"

@app.route('/api/v1/items')
def get_item():
    client = MongoClient(mongo_uri)
    db = client.mydbinstance
    items = db.bigbang
    try:
        query = {}
        projection = {
                "_id":0,
                "item":1,
                "title":1,
                }
        result = list(items.find(query, projection))
    except:
        result = "Failed"
    finally:
        return jsonify({"items":result})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
