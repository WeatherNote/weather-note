---
title: "Google ColaboratoryでPythonを実行してみる"
date: 2023-11-12
categories: 
  - "analysis"
tags: 
  - "python"
  - "データ分析"
  - "環境構築"
coverImage: "f23210a1733b906041051de8bdb678d4.png"
---

本記事ではGoogle Colaboratoryを使う方法について解説します。

**Google Colaboratory を使う前に必要なもの**  
\- Google アカウント

Pythonを触れてみよう！と思った初学者に対して、Google Colaboratoryを利用することを強くすすめています。

なぜならGoogle Colaboratoryは環境構築不要でPythonを使えるからです。

プログラミング初学者がまず環境構築から始める。。となると、つまづく可能性が高く、せっかくPythonで分析作業を進めようと思っても挫折してしまうなんてことも。

また、業務でプログラミングを使ってみたい！という場合、企業にもよりますが、Anacondaなどサードパーティ製品のインストールが制限されていることが多いです。

そのため私はまずGoogle Colaboratoryを使ってPythonに触れてみることをお勧めしています。

Google Colaboratoryは無償で利用することができ、パッケージのダウンロードが不要なうえ、分析に必要なプログラムは基本的には十分です。

では、ここからGoogle Colaboratoryを使う方法について解説していきます。

## Googleアカウントを作成する

まだGoogleアカウントを持っていない場合はGoogleアカウントを作成する必要があります。

![](/weather-note/images/d156e27045ba6b0d41b8e15891c75b9f-1024x649.png)

またはこの[リンク](https://www.google.com/intl/ja/account/about/)からGoogleアカウントを作成するWebサイトに飛びます。

![](/weather-note/images/d9ace4756e49455872b93c1806633383-1024x484.png)

**アカウントを作成する**というアイコンをクリックして作成を開始します。

## Google Colaboratoryを開く

ブラウザでGoogle Colaboratoryと検索します。または、こちらのリンクから[Google Colaboratory](https://colab.research.google.com/?hl=ja)を開いてください。

![](/weather-note/images/b4bf6a69c65cbf52833d16882b6f4fb9-1024x813.png)

右上にあるログインアイコンからログインができればOKです！

![](/weather-note/images/27c269965c904c5cf5bec8e981f771d3-1024x544.png)

ログインを完了すると、以下のようなポップアップ画面が出ますので、左下にあるノートブックを新規作成を**クリック**します。

![](/weather-note/images/Googlecolab_1-1024x571.png)

以下の画面が出てきたらOKです。

![](/weather-note/images/2457bd7d03148557b545c3dca464bf31-1024x554.png)

## Colaboratoryを使ってプログラムを書いてみる

さっそくコードを書いてみましょう！

```
print("Hello Weather!")
```

コードを書いてShift + returnを押すとコードが実行されます。

はじめのコードを実行するときは数秒時間がかかりますが、以下の画像のようにHello Weather!と表示されるはずです。

![](/weather-note/images/ac93bb871f21b05e04983a37b8315faf-1024x538.png)

## Google Colaboratoryにノートブックをダウンロードする方法

最後にノートブックのダウンロードをする方法を紹介します。

左上のファイルタブから**ノートブックをアップロード**をクリックします。

![](/weather-note/images/fe4eaf29628f58ef97b1f1e28014f24c.png)

すると、**ノートブックを開く**というポップアップ画面が表示されるので、**参照ボタン**をクリックして任意のディレクトリに保存したノートブックをアップロードします。

![](/weather-note/images/1a782133328e1bbad7651b72991ae954-1024x782.png)
