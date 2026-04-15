---
title: "Mac (Apple Silicon) とDockerでWRFを実行する方法"
date: 2024-12-23
categories: 
  - "analysis"
tags: 
  - "mac"
  - "python"
  - "wrf"
  - "データ分析"
  - "環境構築"
coverImage: "Screenshot-2024-12-23-at-12.40.00.png"
---

この記事ではMac (Apple Silicon)&Docker環境でWRFを実行する方法を解説します。

環境構築については[こちら](https://www.weathernote.net/20241220-wrf-setup/)の記事をご覧ください。

WRFはWPSとWRF本体の2つの部分に分かれています。

WRFインストールスクリプトを利用した場合はBuild\_WRFの中は以下のようになっているはずです。

```
% ls
```

```
ARWpost  LIBRARIES  WPS-4.6.0  WPS_GEOG  WRF-4.6.1-ARW

ARWpost
```

この前提条件で解説していきます。

なお、今回取り扱うのは2024年9月20日~9月22日に東北地方から西日本にかけて発生した大雨の事例のうち、9/21 00UTC (09JST)から9/22 00UTC (09JST)の期間です。領域は日本付近とし、25kmメッシュで第１領域のみを指定します。

この大雨の事例については、[気象庁の発表資料](https://www.data.jma.go.jp/stats/data/bosai/report/2024/20241029/jyun_sokuji20240920-0922.pdf)をご確認ください。

## **NCARからFNLダウンロードスクリプトを取得**

Mac(コンテナ外）のブラウザで[こちら](https://rda.ucar.edu/datasets/ds083.2/)から2024年9月21日0zから22日0zのファイルを選択し、cshスクリプトをダウンロードします。

  
DATA ACCESSをクリック

![](/weather-note/images/continuing-from-July-1999-1024x526.png)

Web File Listingをクリック

![](/weather-note/images/d8d14d0f506e983d408668b5ba39ad9b-1024x689.png)

Complete File ListのLINKをクリック

![](/weather-note/images/0751964571221a5163796b65924c81ac-1024x490.png)

GRIB2 2024をクリック

![](/weather-note/images/34368c19f2cb14369dbc27eef5cb9188-1024x666.png)

GRIB2 2024.09をクリック（このとき、左にあるチェックボックスにはチェックしない。202409のすべてのデータを選択することになってしまう。）

![](/weather-note/images/0751964571221a5163796b65924c81ac-1-1024x859.png)

必要なデータにチェック

今回の場合は9/21 00UTCから9/22 00UTCまでのデータが必要なので、81から85にチェックをいれます。

![](/weather-note/images/779116e87fc887ff433c18a6db61f08a-1024x412.png)

`fnl_20240921_00_00.grib2`データの場合、9/21の00時00分00秒UTCから05時59分59秒UTCまでのデータが生成できます。  
今回は9/22 00UTCまでの情報を得たいと思っているので、上記の5つダウンロードします。

少し上に戻って、`CSH DOWNLOAD SCRIPT`をクリックすると、ダウンロードができます。

![](/weather-note/images/3e99e23c3051300035686faf40b159b1-1024x228.png)

cshのダウンロードが完了したら、**コンテナ外から**`ubuntu_volume/Build_WRF`にアクセス、FNL\_DATAディレクトリを作ってcshをコピーします。

```
% cd ~/docker/ubuntu_volume/Build_WRF
Build_WRF % mkdir FNL_DATA
FNL_DATA % cp ~/Downloads/rda-download.csh .
FNL_DATA % csh rda-download.csh
```

この後ダウンロードが始まります。しばし待つ。。

lsでディレクトリの中身を確認しましょう。

```
fnl_20240921_12_00.grib2
fnl_20240921_18_00.grib2
fnl_20240921_00_00.grib2	
fnl_20240922_00_00.grib2
fnl_20240921_06_00.grib2	
rda-download.csh
```

上記のようになっていればOK です。

## Ncviewのインストール

Ncviewは生成した土地利用・地形データの中身をクイックで確認するためにインストールします。

```
% brew install ncview   
% brew install --cask xquartz
```

インストールが成功すると以下のようなポップアップが出ます。

![](/weather-note/images/f1c29f8145c8141059f43fd607243891.png)

`Command + space`でXquartzを検索し、起動しておきましょう。

起動しておかないとビューワーにこれから生成する図を表示することができません！

DISPLAY環境変数を設定します。

```
% echo "export DISPLAY=:0" >> ~/.zshrc
% source ~/.zshrc
```

## WPSを使ってデータの前処理

まずWRFを実行する前にWPSでFNLデータを前処理する必要があります。

やることは

- namelist.wpsを編集

- geogrid.exe, ungrib.exe, metgrid.exeの実行

の２つです。

### namelist.wpsの編集

簡単に説明すると、図を描画する領域と期間を指定するためにnamelist.wpsの編集を行います。

**(2025.2.2 追記)この作業はdocker内でも実施可能です。**

```
Build_WRF % cd WPS-4.6.0 
WPS-4.6.0 % nano namelist.wps
```

`% cd ../WPS-4.6.0`でWPS-4.6.0ディレクトリに移動し、namelist.wpsの編集をします。

初期状態のnamelist.wpsは以下のとおりです。

今後namelist.wpsを編集することになりますが、初期状態を忘れてしまった時のために、このブログをブックマークしておいてもいいかもしれません。

```
&share
 wrf_core = 'ARW',
 max_dom = 2,
 start_date = '2019-09-04_12:00:00','2019-09-04_12:00:00',
 end_date   = '2019-09-06_00:00:00','2019-09-04_12:00:00',
 interval_seconds = 10800
/

&geogrid
 parent_id         =   1,   1,
 parent_grid_ratio =   1,   3,
 i_parent_start    =   1,  53,
 j_parent_start    =   1,  25,
 e_we              =  150, 220,
 e_sn              =  130, 214,
 geog_data_res = 'default','default',
 dx = 15000,
 dy = 15000,
 map_proj = 'lambert',
 ref_lat   =  33.00,
 ref_lon   = -79.00,
 truelat1  =  30.0,
 truelat2  =  60.0,
 stand_lon = -79.0,
 geog_data_path = '../WPS_GEOG/'
/

&ungrib
 out_format = 'WPS',
 prefix = 'FILE',
/

&metgrid
 fg_name = 'FILE'
/
```

このうち、変更する変数は以下の13点（今回は動作確認が目的なので、設定変更は必要最小限にとどめます。）

```
 max_dom = 1,
 start_date = '2024-09-21_00:00:00','2019-09-04_12:00:00',
 end_date   = '2019-09-22_00:00:00','2019-09-04_12:00:00',
 interval_seconds = 21600

 e_we              =  100, 220,
 e_sn              =  100, 214,

 dx = 25000,
 dy = 25000,

 ref_lat   =  36.00,
 ref_lon   = 138.00,

 stand_lon = 138.0,

 fg_name = 'FNL’
```

  
修正後のプログラムは以下の通りです。

修正が面倒な場合は以下のプログラムをnamelist.wpsにコピペしちゃってください。

```
&share
 wrf_core = 'ARW',
 max_dom = 1,
 start_date = '2024-09-21_00:00:00','2019-09-04_12:00:00',
 end_date   = '2024-09-22_00:00:00','2019-09-04_12:00:00',
 interval_seconds = 21600
/

&geogrid
 parent_id         =   1,   1,
 parent_grid_ratio =   1,   3,
 i_parent_start    =   1,  53,
 j_parent_start    =   1,  25,
 e_we              =  100, 220,
 e_sn              =  100, 214,
 geog_data_res = 'default','default',
 dx = 25000,
 dy = 25000,
 map_proj = 'lambert',
 ref_lat   =  36.00,
 ref_lon   = 138.00,
 truelat1  =  30.0,
 truelat2  =  60.0,
 stand_lon = 138.0,
 geog_data_path = '../WPS_GEOG/'
/

&ungrib
 out_format = 'WPS',
 prefix = 'FNL', 
/

&metgrid
 fg_name = 'FNL' 
/
```

grib2形式データのリンクを作成します。

**(2025.2.2 追記)この作業はdocker内でも実施可能です。**

```
WPS-4.6.0 % ./link_grib.csh ../FNL_DATA/*grib2
```

### geogrid, ungrib, metgribの実行

以降の作業において、wgrib2のパッケージをインストールが必要になります。  
まだインストールをしていない方は[こちら](https://www.weathernote.net/20240226-wgrib2-xarray/)の記事を参考にwgrib2をインストールしてください。(MacPortsを使うのがおすすめ。)

ここからは**dockerコンテナ内**に入って作業を進めます。`./geogrid`を実行しましょう。

```
ubuntu@41edda1a43e4:~/Build_WRF/WPS-4.6.0$ ./geogrid.exe
```

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!  Successful completion of geogrid.        !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

このような結果が出たら成功です。

また、WPS-4.6.0 ディレクトリに geo\_em.d01.ncというファイルができていることを`ls`で確認しましょう。

第２、第３領域を設定している場合はgeo\_em.d02.nc, geo\_em.d03.ncが生成されます。

Grib2形式のデータのリンクを作成します。

```
ubuntu@41edda1a43e4:~/Build_WRF/WPS-4.6.0$ ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable
```

すると、`GRBFILE.AAA`…などのファイルが作成されます。

ファイル作成を確認したら、./ungrib.exeを実行します。

```
ubuntu@41edda1a43e4:~/Build_WRF/WPS-4.6.0$ ./ungrib.exe
```

こちらも

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!  Successful completion of ungrib.   !

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

という結果が出たらOKです。

引き続き `./metgrid.exe`を実行します。

```
ubuntu@41edda1a43e4:~/Build_WRF/WPS-4.6.0$ ./metgrid.exe
```

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!  Successful completion of metgrid.  !

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

という結果が出たらOKです。

### 作成した領域の確認

コンテナ外に出て、ncviewで先ほど作成したnetcdfデータについて表示したい領域になっているか確認します。

```
WPS-4.6.0 % ncview met_em.d01.2024-09-21_00:00:00.nc
```

プログラムを起動すると、以下のようにNcviewが表示されます。

![](/weather-note/images/variable-TT-1024x930.png)

  
`(15)3d vars`をクリックしながら、`TT`を選択すると、以下のような表示が出るはずです。

![](/weather-note/images/af925fc29ac09cbc77a5ef4dc67c4c50.png)

  
何となく朝鮮半島や日本列島が見えるのがわかると思います。

気温のデータなのですが、デフォルト状態では気温の表示範囲が大きいので、`Range`をクリックして

![](/weather-note/images/variable-TT-1-1024x930.png)

  
Minimumを273.15と変更します。

![](/weather-note/images/0b3fd85a8f761c9b061de27fc02a097a.png)

このような感じで出力ファイルが異常なさそうであればOKです。

絶対値がとてつもなく大きい数が入っている場合は設定がおかしい可能性があります。

## WRFの実行

さて、ここからWRFの実行に入ります。

WRF-4.6.1-ARW/runディレクトリに移動し、namelist.inputを編集します。

**(2025.2.2 追記)この作業はdocker内でも実施可能です。**

```
run % nano namelist.input
```

以下の変数を記載の通り、編集しましょう。

```
 run_days                            = 1,
 run_hours                           = 0,

 start_year                          = 2024, 2019,
 start_month                         = 09,   09,
 start_day                           = 21,   04,
 start_hour                          = 00,   12,
 end_year                            = 2024, 2019,
 end_month                           = 09,   09,
 end_day                             = 22,   06,
 end_hour                            = 00,   00,

 interval_seconds                    = 21600

 dx                                  = 25000,
 dy                                  = 25000,

 max_dom                             = 1,
 e_we                                = 100,    220,
 e_sn                                = 100,    214,

 &namelist_quilt
 nio_tasks_per_group = 1,
 nio_groups = 1,
```

変数の意味については別の記事で解説予定です。

編集が終わったら、  
コンテナ内に戻り、以下のコマンドを実行します。

```
ubuntu@41edda1a43e4:~/Build_WRF/WRF-4.6.1-ARW/run$ ln -s ~/Build_WRF/WPS-4.6.0/met*nc .
```

real.exeを実行します。

```
ubuntu@41edda1a43e4:~/Build_WRF/WRF-4.6.1-ARW/run$ ./real.exe
```

エラーが出なければ、あとは`wrf.exe`を動かすだけです！

シングルコアで計算する場合は

```
ubuntu@41edda1a43e4:~/Build_WRF/WRF-4.6.1-ARW/run$ ./wrf.exe
```

2コアで計算する場合は以下で実行します。 `-np`の後の数字を変更すればコア数を変更することができます。

```
ubuntu@41edda1a43e4:~/Build_WRF/WRF-4.6.1-ARW/run$ mpirun -np 2 ./wrf.exe
```

私が保有するパソコンのスペックにおいて、2コアを使った場合は約30分で計算が終了しました。

コア数を増やすと並列計算ができます。ただ、２コアで計算したからといって、シングルコアの半分の時間で計算が終了するというわけでもないみたいです。

## Pythonを使って降水図を作る

Pythonを利用して以下のプログラムを使って降水マップを作ってみましょう。

私はJupyter Labを使いました。ipynbファイルと同じディレクトリに`wrfout_d01_2024-09-21_12:00:00`のファイルを置いていれば以下のプログラムは動くはずです。

エラーが出る場合は必要なライブラリがインストールされている可能性が低いです。  
特にWRF-python, Cartopy, netCDF4のライブラリをインストールされていない場合は適宜インストールしてください。

```
import numpy as np
import matplotlib.pyplot as plt
from wrf import getvar, latlon_coords, to_np
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# WRFファイルを開く
wrf_file = Dataset('wrfout_d01_2024-09-21_12:00:00')

# 必要な変数を取得
rainnc = getvar(wrf_file, "RAINNC")  # 非対流性降水量
rainc = getvar(wrf_file, "RAINC")    # 対流性降水量
u10 = getvar(wrf_file, "U10")       # 地上10mの東西風速
v10 = getvar(wrf_file, "V10")       # 地上10mの南北風速

# 緯度・経度を取得
lats, lons = latlon_coords(rainnc)

# 総降水量を計算
precip = rainnc + rainc

# プロット
plt.figure(figsize=(12, 8))
ax = plt.axes(projection=ccrs.Mercator())

# 領域全体の緯度・経度を設定
lon_min, lon_max = np.min(to_np(lons)), np.max(to_np(lons))
lat_min, lat_max = np.min(to_np(lats)), np.max(to_np(lats))
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

# 降水量をプロット
levels = np.arange(0, 50, 5)  # 0から50mmまでの範囲で5mm刻み
contour = ax.contourf(to_np(lons), to_np(lats), to_np(precip), levels=levels,
                      transform=ccrs.PlateCarree(), cmap='Blues', extend='both')

# 矢羽根プロット (間引き)
skip = 10  # 矢羽根を間引くための間隔
ax.barbs(to_np(lons[::skip, ::skip]), to_np(lats[::skip, ::skip]),
         to_np(u10[::skip, ::skip]), to_np(v10[::skip, ::skip]),
         transform=ccrs.PlateCarree(), length=6, linewidth=0.6, color='black')

# 海岸線とグリッド線を追加
ax.coastlines(resolution='50m', color='black', linewidth=1)

# グリッド線の設定（破線と内部の線を削除し、ラベルのみ表示）
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linestyle='', color='none')
gl.top_labels = False  # 上側の緯度ラベルを表示しない
gl.right_labels = False  # 右側の経度ラベルを表示しない
gl.xlines = False  # 経度線を非表示
gl.ylines = False  # 緯度線を非表示

# カラーバーの設定
cbar = plt.colorbar(contour, ax=ax, orientation='vertical', pad=0.05)
cbar.set_label('Total Precipitation (mm)')
cbar.set_ticks(np.arange(0, 50, 5))  # 5mm刻みで目盛りを設定

# タイトルを設定
plt.title('Total Precipitation and 10m Wind Barbs')
plt.show()
```

![](/weather-note/images/Screenshot-2024-12-22-at-20.02.06-1024x788.png)

このような図が表示されるはずです。

**能登半島**や**山形県**で大雨になっている様子がわかると思います。

今回はシンプルに第１領域のみの描画を紹介しましたが、今後細かい設定方法を解説予定です。
