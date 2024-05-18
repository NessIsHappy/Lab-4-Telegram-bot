from flask import Flask, request
import requests
import sqlite3
import telebot
from lab3humanfox import identify_picture

app = Flask(__name__)

flagRegister = 0
flagLogin = 0
flagStatus = 0
flagPredict = 0


@app.route("/", methods=["GET", "POST"])
def receive_update():

    global flagRegister
    global flagLogin
    global flagStatus
    global flagPredict

    if request.method == "POST":

        print(request.json)
        chat_id = request.json["message"]["chat"]["id"]
        name = request.json["message"]["from"]["username"]
        try:
            message = request.json["message"]["text"]
        except Exception as e:
            message = None
            bot = telebot.TeleBot('7088127624:AAH6hA1c1sZ6fCMedrXDAIvus2xYj8WN07Q')
            print(request.json)
            file_info = bot.get_file(request.json['message']['photo'][-1]['file_id'])
            print(file_info)

            file_path = file_info.file_path
            downloaded_file = bot.download_file(file_path)

            filename = 'photo.jpg'
            print(filename)
            with open(filename, 'wb') as new_file:
                new_file.write(downloaded_file)

        if message and flagRegister:

            send_message(chat_id, 'Вы зарегистрировались успешно!')
            flagRegister = 0
            flagStatus = 1

            register_database()

            conn = sqlite3.connect('lab3.sql')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, message))
            conn.commit()

            cur.close()
            conn.close()

        if message and flagLogin:

            register_database()

            conn = sqlite3.connect('lab3.sql')
            cur = conn.cursor()
            cur.execute('SELECT * FROM users')
            users = cur.fetchall()

            for el in users:
                if el[1] == name:
                    if el[2] == message:
                        flagStatus = 1
                        send_message(chat_id, 'Вы успешно аутентифицировались!')
                        break
                    else:
                        send_message(chat_id, 'Вы неправильно ввели пароль!')
                        break
                send_message(chat_id, 'Вы не зарегистрированы!')

            flagLogin = 0
            cur.close()
            conn.close()

        if flagPredict and flagStatus:

            print('Predict started!')
            text = identify_picture('train2/', 'valid2/', 'photo.jpg')
            send_message(chat_id, text)
            flagPredict = 0

        if message == '/register':

            register_database()

            conn = sqlite3.connect('lab3.sql')
            cur = conn.cursor()
            cur.execute('SELECT * FROM users')
            users = cur.fetchall()

            flag = 0
            for el in users:
                if el[1] == name:
                    send_message(chat_id, 'Пользователь уже зарегистрирован!')
                    flag = 1

            cur.close()
            conn.close()

            if flag == 0:
                flagRegister = 1
                send_message(chat_id, "Введите пароль:")
        else:
            flagRegister = 0

        if message == '/login':

            if flagStatus:
                send_message(chat_id, "Вы уже в системе!")
            else:
                flagLogin = 1
                send_message(chat_id, "Введите пароль:")
        else:
            flagLogin = 0

        if message == '/logout':

            flagStatus = 0
            send_message(chat_id, "Вы успешно вышли из ситсемы!")

        if message == '/predict':

            if flagStatus:
                flagPredict = 1
                send_message(chat_id, "Отправьте картинку!")
            else:
                send_message(chat_id, "Сначала зайдите!")

    return {"ok": True}


def send_message(chat_id, text):

    method = "sendMessage"
    token = ""
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


def register_database():

    conn = sqlite3.connect('lab3.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users '
                '(id int auto_increment primary key, name varchar(50), pass varchar(50))')
    cur.close()
    conn.close()
