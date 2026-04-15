---
title: "GPV気象データ処理のための事前準備をしよう"
date: 2024-02-26
categories: 
  - "analysis"
tags: 
  - "python"
  - "データ分析"
  - "環境構築"
coverImage: "12f05fafea0bf5dab78e8e700c54484c.png"
---

この記事ではPythonでGRIB2形式のGPVデータを扱うために必要なソフトウェアと、Pythonモジュールのインストール手順を説明します。Macでのインストールについて説明するので、Windowsユーザの方は別の記事をご覧ください。

wgrib2は、アメリカ大気海洋局(NOAA)の気候予測センター(CPC)が開発し公開する、GRIB2形式のファイルを取り扱うためのプログラムで、以下のような機能を持ちます。

- GRIBファイルの作成と読み出し

- データの一部取り出し

- 特定領域の取り出し

- 各種ファイル形式への変換 (ieee, text, binary, CSV, netcdf, mysql)

- 新規データの追記

詳細については以下の [こちら](https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/index.html) を参照して下さい。

## wgrib2をインストールする

Windows用にはコンパイル済みのバイナリファイルが用意されていますが、Macの場合はソースファイルをダウンロードしてコンパイルします。通常のMacには必要なコンパイラがインストールされていません。

Homebrewを使ったインストールもありますが、ここではMacPortsを利用したインストール方法を紹介します。

1. ユーザー名をアルファベットにする

まずはMacを日本語のユーザー名で使用している場合は、新しいアカウントをアルファベットのユーザー名で作成してください。

例　きりたん -> kiritan

設定方法は[こちら](https://support.apple.com/ja-jp/102547)から

2\. MacPortsをインストールする

　[こちら](https://www.macports.org/install.php)のリンクからMacPortsをインストールしましょう。

3\. MacPortsのサイトからコンパイル済みのwgrib2をインストールする。

　MacPortsをインストール後に以下のプログラムをTerminalに入力します。

`sudo port install wgrib2`

これでwgrib2のインストールが完了しました！

## NetCDF4とxarrayをインストールする

Anacondaを使っている場合はcondaでインストールします。

以下のコードをTerminalに入力して実行してください。

```
conda install -c conda-forge netcdf4 xarray dask bottleneck
```

これでNetCDF4とxarrayのインストールが完了しました！

## まとめ

以上のプログラムを順番に実行することでGPV気象データ処理のための事前準備が完了します。
