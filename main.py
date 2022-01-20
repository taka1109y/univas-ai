from selenium import webdriver
import time
import subprocess
import eventlet
import socketio
import threading
import os

#グローバル変数の定義
#スクレイピングのインスタンス生成用
driver = ''

# ChromeOptionsを設定
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument('--start-maximized')
options.add_argument('--kiosk')

# ===============スクレイピング処理=====================================================================================
# スクレイピングの実行処理
def startChrome():
    try:
        global driver
        time.sleep(3)
        print('Starting Chrome...')
        driver = webdriver.Chrome(options=options)# Chromeを起動
        driver.get('http://localhost:3000/')# 指定したURLに遷移
        time.sleep(5)#明示的待機処理

        doAI()
    except Exception as err:#例外エラー発生時
        print(str(err));

def doAI():
    #変数の定義
    global driver
    flag = False
    plist = []
    proc = ''

    # カレントURLを取得し処理分岐
    while True:
        time.sleep(1)
        cur_url = driver.current_url#カレントURLの取得
        #URLのチェック(会議中画面)
        if cur_url == 'http://localhost:3000/meeting' and flag == False:
            try:
                print("starting AI program")
                #AIプログラムの起動
                proc = subprocess.Popen('python3 SpeechRecognition.py', stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                plist.append("{}".format(proc.pid+1))
                time.sleep(1)
                proc = subprocess.Popen('python3 GestureRecognition.py', stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                plist.append("{}".format(proc.pid+1))

                print(plist)#AIプログラムのプロセスID
                flag = True
            except Exception as err:#例外エラー発生時
                print(str(err))
                i = 0
                for item in plist:
                    cmd = 'kill -9 ' + str(plist[i])
                    subprocess.call(cmd, shell=True)
                    i += 1
                del plist[:]#プロセスID用の配列の初期化
                continue

        #URLのチェック(会議終了後、待機画面)
        elif cur_url == 'http://localhost:3000/' and len(plist) != 0:
            print("Leave the meeting.")
            try:
                #各AIプログラムの停止
                i = 0
                for item in plist:
                    cmd = 'kill -9 ' + str(plist[i])
                    subprocess.call(cmd, shell=True)
                    i += 1
                del plist[:]#プロセスID用の配列の初期化
                flag = False
            except Exception as err:#例外エラー発生時
                print(str(err))

# ===============スクロール処理(soketio)=====================================================================================
sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def catchScroll(sid, data):
    print('sid: ' + sid + ',data: ' + data)
    scrollRun(data)

#サーバー起動
def socket():
    eventlet.wsgi.server(eventlet.listen(('192.168.2.100', 5000)), app)

#スクレイピングによるスクロール処理
def scrollRun(msg):
    global driver
    try:
        if(msg == 'up'):
            driver.execute_script("document.querySelector('.talk').scrollTop -= 100")
        elif(msg == 'down'):
            driver.execute_script("document.querySelector('.talk').scrollTop += 100")
    except Exception as err:#例外エラー発生時
        print(str(err))


# ===============実行=====================================================================================
if __name__ == '__main__':
    thread_1 = threading.Thread(target=socket)
    thread_2 = threading.Thread(target=startChrome)

    thread_1.start()
    thread_2.start()

