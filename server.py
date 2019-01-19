from flask import Flask, render_template,request
import requests
from time import ctime
from bs4 import BeautifulSoup
import sqlite3 as lite


app = Flask(__name__)

@app.route('/')
def index():
    """
    main page 라우트
    페이지 접속요청시 n사 실시간 키워드를 requests, BeautifulSoup를 활용하여
    수집 한 뒤, 응답으로 수행 시간과 키워드를 반환
    """
    naver_uri = "https://www.naver.com/"
    executed_time = ctime()
    naver_html = requests.get(naver_uri).text

    soup = BeautifulSoup(naver_html, 'html.parser')
    kw_ul = soup.find('ul', attrs={'class':'ah_l'})
    keywords = [li.text for li in kw_ul.find_all('span', attrs={'class':'ah_k'})]

    return render_template('index.html', time=executed_time, keywords=keywords)

@app.route('/user/<string:name>')
def user(name=None):
    """
    user의 path로 어떤 문자열 입력시 그 문자열을 응답의 msg로 반환하여 템플리팅에 참조
    """
    return render_template('user.html', msg=name)

@app.route('/users')
def users():
    """
    /users?uid=1234&upw=1q2w3e4r 에서
    요청의 arguments를 수집하여 쿼리스트링을 응답의 rows로 반환
    """
    keywords = request.args
    return render_template('users.html', rows=keywords )

@app.route('/movies', methods=["GET","POST"])
def movies():
    """
    movies의 method가 get일 경우 data.db의 모든 자료를 선택하여 반환.
    위 users,user 사례와 조합시 조건을 부여하는데 사용가능
    movies의 method가 post일 경우 사용자가 form 태그에서 입력한 값을 data.db에 입력
    """
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

# TODO: mlab의 bigbang collections 에 접근하여 모든 아이템 출력하기

#@app.route('/api/v1/items')
#def get_item():
    #return은 json 타입으로!!

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
