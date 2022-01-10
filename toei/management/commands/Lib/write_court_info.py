import gspread
import json
import sys
from django.conf import settings
import re

class WriteCourtInfo:

    @staticmethod
    def write_scc(get_courts):

        #ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
        from oauth2client.service_account import ServiceAccountCredentials

        #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

        #認証情報設定
        #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
        credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.CSV_FILE_SCC, scope)

        #OAuth2の資格情報を使用してGoogle APIにログインします。
        gc = gspread.authorize(credentials)

        #共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
        SPREADSHEET_KEY = '1aRFnIywzm0jeylKh0_vnUHTI9Xf56VMxglj3Lg1Tp-4'

        court_info = ""
        for get_court in get_courts:
            time = str(get_court["from_time"]) + '-' + str(get_court["to_time"])
            if court_info.find(time) == -1:
                court_info += time + '\n'
            court_info += get_court["user_nm_kn"] + ' ' + str(get_court["count"]) + '件\n'

        print("----------------------\n", court_info.rstrip("\n"))

        # 共有設定したスプレッドシートのシート1を開く
        worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(str(get_courts[0]["month"]) + '月管理表')
        row = 1
        line = 1
        print(get_court["day"])
        for i in range(4, 22, 6):
            for j in range(4, 204, 40):
                import_value = worksheet.cell(j, i).value
                if import_value != "":
                   day = re.match(r'.*月(\d+)日.*', import_value).group(1)
                   if int(day) == get_court["day"]:
                       row = j
                       line = i
                       print(j)
                       print(i)
        # import_value = worksheet.acell('D4').value
        # print(import_value)
        worksheet.update_cell(row+32, line+2, court_info.rstrip("\n"))
        # for (var i=d; i <= p; i = i+6) {
        #     for (var i=4; i <= lastRow; i = i+40) {
        # #A1セルの値を受け取る
        # import_value = int(worksheet.acell('A1').value)

        # #A1セルの値に100加算した値をB1セルに表示させる
        # export_value = import_value+100
        #worksheet.update_cell(1,1, 100)