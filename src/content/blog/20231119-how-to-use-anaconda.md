---
title: "Anacondaを使ってPythonの環境構築をしよう"
date: 2023-11-19
categories: 
  - "analysis"
tags: 
  - "python"
  - "データ分析"
  - "環境構築"
coverImage: "db50263dff9149c3b1d90993cf076e42.png"
---

Pythonを使ったデータ分析をする時に、Google Colaboratoryを使うのもいいですが、慣れてきたら自分のパソコンでもPythonが使えるように環境設定にもチャレンジしてみましょう。

Google Colaboratoryを使う方法は[こちらの記事](https://www.weathernote.net/20231112-how-to-use-googlecolaboratory/)をご覧ください。

この記事ではAnacondaを使ったPythonの環境構築から、Jupyter Notebookの起動までの流れを説明します。

Mac PCにおけるダウンロード方法を紹介していますが、Windowsでも基本操作は変わりません。

## Anacondaのダウンロードとインストール

[こちらのリンク](https://www.anaconda.com/products/individual)から、ダウンロードサイトに行きます。

以下のような画面に遷移するはずです。

![](/weather-note/images/6f7cbf7367b293a40e87b969e99a1876-1024x497.png)

アップルロゴの入ったDownloadアイコンの右にある∨ボタンをクリックすると、IntelかM1/M2を選択することができます。

ご自身のMacに合わせて選択してクリックします。

するとダウンロードが始まります。

ダウンロード先にある「Anaconda3-2023.09-0-MacOSX-arm64.pkg」を実行し、インストールを行います。

＊ファイル名の「2023.09」はダウンロードしたタイミングにより変わることがあります。

インストール後、「**Anaconda Navigator**」というソフトが使えるようになります。

## Anacondaの起動

Anacondaは「アプリケーション」から起動できます。

メニューバーの「移動」から「アプリケーション」に移動し、「**Anaconda Navigator**」を選んで起動してください。初回起動時 は少し時間かかるかもしれません。

![](/weather-note/images/66555d13f0bc84f3bd646fe4d390f3fe-1024x593.png)

![](/weather-note/images/2783f82c0ac8f26fc867e994eaa0eeaf-1024x354.png)

初回起動時は以下のようにLog inを求められることがあるかもしれませんが、右上のx印をクリックして構いません。

![](/weather-note/images/5ca084c713ed12403860aa1502eef502-1024x901.png)

## Jupyter Notebookの起動

起動すると、以下のような画面になります。

![](/weather-note/images/e1bb035d73e5b4e4d06e2631ca27c225-1024x582.png)

Jupyter Notebookを見つけて**「Launch」**アイコンをクリックします。

しばらくするとブラウザが立ち上がり、以下のような画面になります。

![](/weather-note/images/336da21fa3d01064a78aa8b82cea5c78-1024x303.png)

これでJupyter Notebookを使う準備は完了です！

## Jupyter Notebookでプログラムを書いてみる

では、Jupyter Notebookを使ってプログラムを書いてみましょう。

Jupyter Notebookを新規で開く場合は、右上にある「新規」アイコンからPython(ipykernel)をクリックします。

![](/weather-note/images/8af66f12fc612ba91ddb9e07d6c8af18-1024x307.png)

すると、以下のようにノートブックが開きます。

![](/weather-note/images/99f66966a62ccbda29c3c2bca48f1cfc-1024x200.png)

試しに以下のプログラムを実行してみましょう。

```
print("Hello Weather!")
```

実行はセルの上にある**「▶︎実行」**アイコンをクリックするか、**ctrl + return**を押します。

すると、以下のように実行結果が出力されるはずです。

![](/weather-note/images/036b8b811c09faaa5607eb6fdec6684c-1024x247.png)

ノートブックを保存するには**command + s**を押します。

ファイルを閉じる場合は「**ファイル**」→「**閉じて終了**」を選択します。

![](/weather-note/images/632d7711f3483f92b686207f9e221695-1024x502.png)
