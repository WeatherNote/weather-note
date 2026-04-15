---
title: "Apple Silicon MacBook AirにWRF 4.6.1をインストールする【実録・つまずき解決付き】"
date: 2026-04-06
categories: 
  - "analysis"
  - "研究・自己研鑽"
tags: 
  - "mac"
  - "python"
  - "wrf"
  - "データ分析"
  - "環境構築"
coverImage: "thumbnail.png"
---

## はじめに

気象数値モデル WRF（Weather Research and Forecasting model）は、研究・教育現場で広く使われていますが、**MacBook Air（Apple Silicon / M系チップ）への導入は情報が少なく、独自のつまずきポイントが多い**のが現状です。

この記事では、実際にWRF 4.6.1 + WPS 4.6.0をMacBook Air（M系 / macOS）に導入した際の手順を、**エラーと対処も含めて丸ごと記録**しています。

「Linuxでは動かしたことがあるけど、Macだと勝手が違う…」という方の参考になれば幸いです。

## 動作確認環境

| 項目 | 内容 |
| --- | --- |
| マシン | MacBook Air（Apple Silicon / arm64） |
| OS | macOS 26.x |
| CPU | 8コア |
| メモリ | 16 GB |
| ストレージ空き | 130 GB以上 |
| WRFバージョン | 4.6.1 |
| WPSバージョン | 4.6.0 |
| 並列方式 | MPI（dmpar）/ 8コア |
| PBLスキーム | MYNN（bl\_pbl\_physics=5） |

## 全体の流れ

```
1. 必要ライブラリのインストール（Homebrew）
2. WRFソースコードのダウンロード・展開
3. WPSソースコードのダウンロード・展開
4. 環境変数の設定
5. WRFのconfigure・コンパイル
6. WPSのconfigure・コンパイル（ハマりポイントあり）
7. WPS地形データ（geogデータ）のダウンロード・展開
```

![](/weather-note/images/01_wrf_system_flow-1-1024x509.png)

## 1\. Homebrewの確認と必要ライブラリのインストール

Apple SiliconのMacでは、Homebrewは `/opt/homebrew/` にインストールされています（Intel Macは `/usr/local/`）。

```
# Homebrewのパスを通す（Apple Silicon）
eval "$(/opt/homebrew/bin/brew shellenv)"

# インストール済みパッケージを確認
brew list | grep -E "gcc|mpich|open-mpi|netcdf|hdf5|jasper|libpng"
```

### 必要なパッケージ

WRFのコンパイルには以下が必要です。

| パッケージ | 用途 |
| --- | --- |
| gcc（gfortran含む） | Fortranコンパイラ |
| open-mpi | MPI並列処理 |
| netcdf / netcdf-fortran | NetCDF I/O |
| hdf5 | NetCDF-4/HDF5サポート |
| jasper | GRIB2のJPEG2000圧縮対応（WPS用） |
| libpng | GRIB2のPNG圧縮対応（WPS用） |

未インストールのものはまとめてインストールします。

```
brew install gcc open-mpi netcdf netcdf-fortran hdf5 jasper libpng
```

* * *

### ⚠️ つまずきポイント①：gccバージョンアップによるnetcdf-fortranのABI不一致

`open-mpi` をインストールした際、依存関係で **gcc が 14.x → 15.x にアップグレード**されました。  
しかし既存の `netcdf-fortran` は古いgccでビルドされたボトル（バイナリ）だったため、ABI（バイナリインターフェース）が合わなくなります。

**対処法：netcdf-fortranを再インストールする**

```
brew reinstall netcdf-fortran
```

これで最新のgccに合ったバイナリが再取得されます。

## 2\. WRF・WPSのソースコードを取得

```
mkdir -p ~/WRF
cd ~/WRF

# WRF 4.6.1
curl -L https://github.com/wrf-model/WRF/releases/download/v4.6.1/v4.6.1.tar.gz \
     -o WRF-4.6.1.tar.gz

# WPS 4.6.0（GitHubアーカイブを使う）
curl -L https://github.com/wrf-model/WPS/archive/refs/tags/v4.6.0.tar.gz \
     -o WPS-4.6.0.tar.gz

# 展開
tar xzf WRF-4.6.1.tar.gz
tar xzf WPS-4.6.0.tar.gz
```

> **注意：** WPS の GitHub Release ページにある `v4.6.0.tar.gz` のダウンロードリンクは404になる場合があります。`/archive/refs/tags/` のURLを使ってください。

## 3\. 環境変数の設定

WRFのconfigure・コンパイルには多くの環境変数を正しく設定する必要があります。  
毎回手打ちするのは大変なので、スクリプトにまとめておくと便利です。

```
cat > ~/WRF/env_wrf.sh << 'EOF'
#!/bin/bash
# WRF/WPS 環境変数設定スクリプト
# source env_wrf.sh で読み込む

eval "$(/opt/homebrew/bin/brew shellenv)"

# ディレクトリ
export WRFDIR=~/WRF/WRFV4.6.1
export WPSDIR=~/WRF/WPS-4.6.0

# コンパイラ（Homebrew GCC）
export CC=gcc-15
export CXX=g++-15
export FC=gfortran-15
export F77=gfortran-15
export F90=gfortran-15

# NetCDF（WRFはinclude/libが1つのパスにあることを期待するため結合）
export NETCDF=~/WRF/netcdf_combined
export HDF5=/opt/homebrew/opt/hdf5

# Jasper（WPS のGRIB2対応）
export JASPERLIB=/opt/homebrew/opt/jasper/lib
export JASPERINC=/opt/homebrew/opt/jasper/include

# WRF設定
export WRF_EM_CORE=1
export WRFIO_NCD_LARGE_FILE_SUPPORT=1

# macOS 向け
export LDFLAGS="-L/opt/homebrew/opt/netcdf-fortran/lib \
  -L/opt/homebrew/opt/netcdf/lib \
  -L/opt/homebrew/opt/hdf5/lib \
  -L/opt/homebrew/opt/jasper/lib \
  -L/opt/homebrew/opt/libpng/lib"
export CPPFLAGS="-I/opt/homebrew/opt/netcdf-fortran/include \
  -I/opt/homebrew/opt/netcdf/include \
  -I/opt/homebrew/opt/hdf5/include \
  -I/opt/homebrew/opt/jasper/include \
  -I/opt/homebrew/opt/libpng/include"

# スタックサイズ制限解除（WRF実行に必須）
ulimit -s unlimited
EOF
```

### ⚠️ つまずきポイント②：NetCDF の include/lib を1か所に集める

WRFの configure スクリプトは `$NETCDF/include` と `$NETCDF/lib` の下に  
NetCDF-C と NetCDF-Fortran の両方のファイルがあることを期待します。  
しかしHomebrewではそれぞれ別の場所にインストールされているため、  
**結合ディレクトリを手作業で作成**する必要があります。

```
mkdir -p ~/WRF/netcdf_combined/include
mkdir -p ~/WRF/netcdf_combined/lib

# NetCDF-C のヘッダ・ライブラリ
cp /opt/homebrew/opt/netcdf/include/*.h  ~/WRF/netcdf_combined/include/
cp /opt/homebrew/opt/netcdf/lib/libnetcdf.* ~/WRF/netcdf_combined/lib/

# NetCDF-Fortran のヘッダ・モジュール・ライブラリ
cp /opt/homebrew/opt/netcdf-fortran/include/*.mod \
   ~/WRF/netcdf_combined/include/ 2>/dev/null || true
cp /opt/homebrew/opt/netcdf-fortran/lib/libnetcdff.* \
   ~/WRF/netcdf_combined/lib/

# netcdf.inc（Fortran用インクルードファイル）が別途必要
cp /opt/homebrew/Cellar/netcdf-fortran/4.6.2/include/netcdf.inc \
   ~/WRF/netcdf_combined/include/
```

## 4\. WRFのconfigure・コンパイル

```
source ~/WRF/env_wrf.sh
cd ~/WRF/WRFV4.6.1

# configure（対話式）
./configure
```

表示される選択肢の中から以下を選びます。

```
Select from among the following Darwin ARCH options:
  ...
  33. (serial)  34. (smpar)  35. (dmpar)  36. (dm+sm)  GNU (gfortran/gcc): Open MPI

Enter selection [1-36] : 35    ← MPI並列 + gfortran + Open MPI
Compile for nesting? [default 1]: 1  ← 基本ネスティング
```

| 選択肢 | 意味 |
| --- | --- |
| 35（dmpar） | MPI分散並列（複数コアで計算） |
| 36（dm+sm） | MPI+OpenMPハイブリッド（MacBook Airでは35が安定） |

configure成功後、8コアでコンパイルします（30〜60分程度かかります）。

```
./compile -j 8 em_real > compile_wrf.log 2>&1
```

完了したら実行ファイルを確認します。

```
ls -lh main/wrf.exe main/real.exe main/ndown.exe
```

3ファイルが生成されていれば成功です。

## 5\. WPSのconfigure・コンパイル

```
source ~/WRF/env_wrf.sh
export WRF_DIR=~/WRF/WRFV4.6.1
cd ~/WRF/WPS-4.6.0

./configure
```

選択肢から以下を選びます。

```
19. Darwin Intel gfortran/gcc (dmpar)  ← GRIB2対応あり・MPI並列
```

> **ポイント：** `_NO_GRIB2` が付かない番号を選ぶことで、  
> NCEP FNL などのGRIB2形式データが処理できます。

```
./compile > compile_wps.log 2>&1
```

### ⚠️ つまずきポイント③：ungrib.exe のリンクエラー（jasper 4.x のAPI変更）

WPSコンパイル後、`geogrid.exe` と `metgrid.exe` は生成されるが、  
**`ungrib.exe` だけ生成されない**というエラーが発生しました。

```
ld: symbol(s) not found for architecture arm64:
  "_jpc_decode", referenced from: _dec_jpeg2000_ in libg2_4.a
```

**原因：** WPS内蔵のg2ライブラリが参照している `jpc_decode` / `jpc_encode` 関数が、  
jasper 4.x では**プライベートシンボル**（非公開）になったため、リンクできなくなっています。

**対処法：** WPS内蔵の `dec_jpeg2000.c` と `enc_jpeg2000.c` を  
jasper 4.x の公開API（`jas_image_decode` / `jas_image_encode`）を使うように書き直します。

また、同時に `configure.wps` の `COMPRESSION_LIBS` に libpng のパスが抜けていることも  
別のリンクエラーの原因でした。

```
# configure.wps の修正
# 変更前
COMPRESSION_LIBS = -L/opt/homebrew/opt/jasper/lib -ljasper -lpng -lz

# 変更後
COMPRESSION_LIBS = -L/opt/homebrew/opt/jasper/lib \
                   -L/opt/homebrew/opt/libpng/lib \
                   -L/opt/homebrew/opt/zlib/lib \
                   -ljasper -lpng -lz
```

`dec_jpeg2000.c` の核心部分の修正：

```
/* 旧API（jasper 1.x/2.x） */
image = jpc_decode(jpcstream, opts);   // ← jasper 4.x では非公開

/* 新API（jasper 4.x） */
int fmt = jas_image_strtofmt("jpc");
image = jas_image_decode(jpcstream, fmt, NULL);  // ← 公開API
```

修正後に再コンパイルすると、3つの実行ファイルが揃います。

```
ls -lh *.exe
# geogrid.exe -> geogrid/src/geogrid.exe
# metgrid.exe -> metgrid/src/metgrid.exe
# ungrib.exe  -> ungrib/src/ungrib.exe
```

## 6\. WPS地形データ（geogデータ）のダウンロード

WPSで地形・土地利用データを処理するには、NCARが配布している静的地形データが必要です。  
ソースコードとは別にダウンロードします。

```
mkdir -p ~/WRF/WPS_GEOG
cd ~/WRF/WPS_GEOG

BASE="https://www2.mmm.ucar.edu/wrf/src/wps_files"

# 必須データ（約2.6GB）
curl -L $BASE/geog_high_res_mandatory.tar.gz -o geog_high_res_mandatory.tar.gz

# Noah-MP陸面モデル用（約1.9GB）
curl -L $BASE/geog_noahmp.tar.gz -o geog_noahmp.tar.gz

# Thompson雲微物理用エアロゾルデータ
curl -L $BASE/geog_thompson28_chem.tar.gz -o geog_thompson28_chem.tar.gz

# MODIS高解像度土地利用（15秒）
curl -L $BASE/modis_landuse_20class_15s_with_lakes.tar.gz \
     -o modis_landuse_20class_15s_with_lakes.tar.gz

# その他（都市・代替陸面など）
curl -L $BASE/geog_urban.tar.gz -o geog_urban.tar.gz
curl -L $BASE/geog_older_than_2000.tar.gz -o geog_older_than_2000.tar.gz
curl -L $BASE/geog_alt_lsm.tar.gz -o geog_alt_lsm.tar.gz
```

> **データ量の目安：** 合計で約7〜8GB（展開後はさらに大きくなります）。  
> ディスクに余裕を持たせてください。

```
# 並行展開
for f in *.tar.gz; do tar xzf "$f" & done
wait

# WPS_GEOG サブディレクトリが作られた場合は統合する
mv ~/WRF/WPS_GEOG/WPS_GEOG/* ~/WRF/WPS_GEOG/ 2>/dev/null
rmdir ~/WRF/WPS_GEOG/WPS_GEOG 2>/dev/null
```

## 7\. namelist.wps の geog\_data\_path を設定

```
# ~/WRF/WPS-4.6.0/namelist.wps の該当行を編集
geog_data_path = '/Users/ユーザー名/WRF/WPS_GEOG/'
```

## まとめ：Macでつまずくポイント一覧

| # | 問題 | 原因 | 対処 |
| --- | --- | --- | --- |
| 1 | `netcdf-fortran` のリンクエラー | open-mpi導入でgccがアップグレード → ABI不一致 | `brew reinstall netcdf-fortran` |
| 2 | `netcdf.inc` が見つからない | Homebrewの分散インストール構成 | 結合ディレクトリを手作成 |
| 3 | `ungrib.exe` が生成されない | jasper 4.xで`jpc_decode`が非公開化 | `dec/enc_jpeg2000.c` を新APIで書き直し |
| 4 | `libpng` のリンクエラー | `configure.wps` にパスが含まれていない | `COMPRESSION_LIBS` にlibpngパスを追加 |
| 5 | `real.exe` が `FATAL` で終了 | `ra_lw/sw_physics` が全ドメインで異なる値 | `namelist.input` で全ドメイン統一 |

## おわりに

Apple Silicon Mac へのWRF導入は、特に **jasper 4.x とのAPI非互換** という  
ネット上にほとんど情報がないつまずきポイントがあります。  
この記事がその解決の参考になれば幸いです。

WPS・WRFが揃えば、NCEP FNL データを使った実際の気象シミュレーションが可能になります。

## 参考リンク

- [WRF公式ユーザーガイド](https://www2.mmm.ucar.edu/wrf/users/)

- [WRF GitHub リポジトリ](https://github.com/wrf-model/WRF)

- [WPS geogデータ一覧（NCAR/MMM）](https://www2.mmm.ucar.edu/wrf/users/download/get_sources_wps_geog.html)

- [Homebrew](https://brew.sh/)
