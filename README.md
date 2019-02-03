# pyEkikara
えきから時刻表の「駅時刻表」をスクレイピングするスクリプト
(A scraping script for "Eki-kara Jikoku-hyo" station timetables)

![ss](https://user-images.githubusercontent.com/46576737/52183480-39ef9d00-27d6-11e9-8769-13338607ea67.png)

# 開発環境 （Dependency）
- Python 3.6
- Beautiful Soup 4

# 使い方 （Usage）

## 実行方法 （How to run）

`python pyEkikara.py URL [--no-details] [--verbose]`

- `URL` (Required): 駅時刻表のURL (A station timetable URL)
- `--no-details` : 列車詳細情報を取得しない (No train details)
- `--verbose`: 処理の詳細を表示する (Show process details)

例（Example）:
`python pyEkikara.py 
http://ekikara.jp/newdata/ekijikoku/1301131/up1_14103021.htm --verbose`

横浜駅の東海道線平日上り時刻表のデータを、各列車の詳細情報を含めて取得します。 (This example shows how to acquire the Tokaido line Yokohama station timetable for Tokyo direction on weekdays, including train details.)

## 出力データ (Outputs)

取得結果はCSVとJSONで保存されます。JSONには各列車のダイヤなど、CSVよりも詳細なデータを含みます。 (Acquired results are saved as CSV and JSON format. JSON format data are in more detailed in that they include each train schedule.)

# ライセンス（License）
このスクリプトはMITライセンスのもとで公開されています。詳細はLICENSEをご覧ください。(This software is released under the MIT License, see LICENSE.)
