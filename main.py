import datetime
import time
from flask import Flask, request, abort
import parameter
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import requests
import http.cookiejar as cookielib
import json
mafengwoSession = requests.session()
mafengwoSession.cookies = cookielib.LWPCookieJar(filename="mafengwoCookies.txt")

app = Flask(__name__)

line_bot_api = LineBotApi(parameter.LineBot_Channel_Access_Token)
handler = WebhookHandler(parameter.LineBot_Channel_Secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    line_bot_api.push_message(parameter.Reply_token, TextSendMessage(text=body))
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def getIndex():
    responseRes = mafengwoSession.get("https://tw.screener.finance.yahoo.net/future/q?type=tick&perd=1m&mkt=01&sym=WTX%26")
    mafengwoSession.cookies.save()
    JsonResponseRes = responseRes.text.replace("null(","").replace(");","").replace("sections",'"sections"')
    # return json.loads(JsonResponseRes)['mem']['103']
    The_Begin_index = JsonResponseRes.find('"103":')+6
    The_End_index = The_Begin_index+7
    return JsonResponseRes[The_Begin_index:The_End_index]


if __name__ == "__main__":
    Begin_Index = getIndex()
    line_bot_api.push_message(parameter.Reply_token, TextSendMessage(text=Begin_Index))

    while True:
        try:
            Now_Index = getIndex()
            Different = float(Now_Index) - float(Begin_Index)
            if Different > 15 or Different < -15:
                Begin_Index = Now_Index
                if Different > 30 or Different < -30:
                    line_bot_api.push_message(parameter.Reply_token, TextSendMessage(text='大波動 ! ! '+str(Begin_Index)))
                else:
                    line_bot_api.push_message(parameter.Reply_token, TextSendMessage(text=Begin_Index))
            print(datetime.datetime.now())
            time.sleep(120)

            ##11點後停止
            theTime = datetime.datetime.now().strftime('%H%M')
            dayOfWeek = datetime.datetime.now().weekday()

            if int(theTime) > 2345 and dayOfWeek < 4: #星期五的1045不停
                print('休息3600*9')
                hoursec = 3600 * 9
                time.sleep(hoursec)
                # exit()
            if dayOfWeek == 5 or dayOfWeek == 6:
                print('休息3600*24')
                time.sleep(3600*24)
            if dayOfWeek == 0 and int(theTime) < 100:
                print('休息3600*8+45*60')
                time.sleep(3600*8+45*60)
        except Exception as E :
            print(E)
            time.sleep(60)
