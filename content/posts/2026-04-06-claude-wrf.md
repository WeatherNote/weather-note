---
title: "Claude Codeにプロンプト1つを貼るだけ！Apple Silicon MacにWRF環境を一撃構築する方法"
date: 2026-04-06
categories: 
  - "analysis"
  - "研究・自己研鑽"
tags: 
  - "claude"
  - "mac"
  - "python"
  - "wrf"
  - "データ分析"
  - "環境構築"
coverImage: "thumbnail_claude.png"
---

## はじめに

WRF（Weather Research and Forecasting Model）のインストールは、Linux 環境でも決して簡単ではありません。ましてや **Apple Silicon Mac（M1/M2/M3）** となると、さらに難易度が跳ね上がります。jasper 4.x の API 変更、netcdf\_combined ディレクトリ問題、GCC バージョン依存など、Mac 固有の落とし穴が数多く存在します。

そこで今回は、Anthropic が提供する CLI ベースの AI コーディングエージェント **Claude Code** を活用して、プロンプト1つで WRF + WPS の環境を全自動構築する方法を紹介します。実際に使用したプロンプトの全文と、構築中に起きたことを包み隠さず共有します。

## Claude Code とは

**Claude Code** は、Anthropic が提供する CLI ベースの AI コーディングエージェントです。ターミナル上で動作し、コマンドの実行・ファイルの編集・エラーへの対処を自律的に行います。単なるコード補完ツールではなく、「複雑な環境構築タスクをエンジニアの代わりにこなす」ことができる点が大きな特徴です。

Claude Codeの記事は検索するとたくさん出てくると思いますので、ここでは割愛します。

## 全体フロー

![](/weather-note/images/cc_fig1_flow-1024x556.png)

## なぜ Apple Silicon Mac での WRF 構築は難しいのか

WRF を Mac に入れようとして挫折した経験がある人は少なくないでしょう。主な難しさを以下に整理します。

1. **netcdf\_combined ディレクトリの手動作成が必要**  
    WRF のビルドシステムは NetCDF-C と NetCDF-Fortran のヘッダ・ライブラリが1つのディレクトリにまとまっていることを前提としています。Homebrew でインストールすると別々のパスに配置されるため、手動で統合ディレクトリを作る必要があります。

3. **jasper 4.x で jpc\_decode / jpc\_encode がプライベート化**  
    WPS に含まれる `dec_jpeg2000.c` / `enc_jpeg2000.c` は jasper 3.x 以前の内部 API を直接呼び出しています。jasper 4.x ではこれらがプライベート化されたため、`ungrib.exe` のリンク時にシンボルエラーが発生します。

5. **GCC バージョンが Homebrew の更新で変わると ABI ミスマッチが発生**  
    Homebrew で gcc をアップデートすると、コンパイル済みの netcdf-fortran などと ABI（Application Binary Interface）が合わなくなる場合があります。環境変数に固定バージョン番号を明示することが重要です。

7. **configure の選択番号が環境によって変わる**  
    `./configure` を実行すると選択肢の番号が表示されますが、インストール済みのコンパイラやライブラリの状況によって番号が変わります。スクリプトで固定値を渡すとミスマッチが起きることがあります。

9. **WPS の GitHub releases URL が 404 になることがある**  
    WPS の特定バージョンは GitHub の releases ページに存在せず、`archive/refs/tags/` の URL からダウンロードする必要があります。公式ドキュメントの URL をそのままコピーすると 404 エラーになるケースがあります。

## 実際に使ったプロンプト

以下が、Claude Code に貼り付けたプロンプトの全文です。そのままコピーしてお使いください。

![](/weather-note/images/cc_fig3_prompt_anatomy-1024x634.png)

```
Apple Silicon（arm64）MacBook に WRF + WPS の
気象シミュレーション環境を一から構築してください。

【ユーザー設定（最初に確認してください）】
- WRF バージョン: 4.6.1
- WPS バージョン: 4.6.0
- 作業ディレクトリ: ~/WRF/
- 使用コア数: 8
- シミュレーション種別: 実データ（FNL等）と理想実験の両方
- 希望する物理スキーム: MYNN PBL

【ステップ 1: 事前確認】
以下を確認してから進めること：
1. Homebrew がインストール済みか確認
   $ which brew
   → 未インストールなら以下を実行：
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Xcode Command Line Tools が入っているか確認
   $ xcode-select -p
   → 未インストールなら: xcode-select --install
3. 現在の gcc / gfortran バージョンを確認
   $ brew info gcc

【ステップ 2: 依存ライブラリのインストール】
以下を Homebrew でインストールする：
brew install gcc open-mpi netcdf netcdf-fortran hdf5 jasper libpng zlib wget

【ステップ 3: 環境変数スクリプト（env_wrf.sh）の作成】
~/WRF/env_wrf.sh を作成する。
gcc バージョンは brew info gcc で確認した番号を使うこと。
export CC=gcc-XX / export FC=gfortran-XX
export NETCDF=$HOME/WRF/netcdf_combined
export HDF5=/opt/homebrew/opt/hdf5
export JASPER_INC / JASPER_LIB を設定
ulimit -s unlimited

【ステップ 4: netcdf_combined ディレクトリの作成】
mkdir -p ~/WRF/netcdf_combined/{include,lib}
NetCDF-C と NetCDF-Fortran の include・lib を統合する。
netcdf.inc が存在しない場合は手動コピーすること。

【ステップ 5: WRF のダウンロードとコンパイル】
GitHub から v4.6.1 をダウンロードし、
./configure で「GNU gfortran/gcc: Open MPI, dmpar」を選択。
./compile em_real でコンパイル。
wrf.exe / real.exe / ndown.exe の3ファイルが生成されれば成功。

【ステップ 6: WPS のダウンロードとコンパイル】
archive/refs/tags/ URL からダウンロード（releases URL は404になる場合あり）。
jasper 4.x API 対応として dec_jpeg2000.c と enc_jpeg2000.c を書き直す：
- jpc_decode() → jas_image_decode()
- jpc_encode() → jas_image_encode()
- 構造体直接アクセス → 公開 API（jas_image_numcmpts 等）に変更
configure.wps の COMPRESSION_LIBS に libpng パスを追加。
geogrid.exe / metgrid.exe / ungrib.exe の3ファイルが生成されれば成功。

【ステップ 7: 地形データのダウンロード】
https://www2.mmm.ucar.edu/wrf/users/download/get_sources_wps_geog.html
から完全高解像度セットを取得し ~/WRF/WPS_GEOG/ に展開する。

【完了チェックリスト】
□ wrf.exe / real.exe / ndown.exe が存在する
□ geogrid.exe / metgrid.exe / ungrib.exe が存在する
□ WPS_GEOG に地形データが展開されている

【トラブルシューティング】
| エラー | 原因 | 対処 |
|--------|------|------|
| netcdf.inc not found | netcdf_combined 不完全 | netcdf.inc を手動コピー |
| _jpc_decode undefined | jasper 4.x API 変更 | dec/enc_jpeg2000.c を書き直し |
| libpng not found | configure.wps の COMPRESSION_LIBS 不足 | libpng パスを追加 |
| real.exe FATAL | ra_lw/sw_physics 全ドメイン不一致 | 全ドメイン同一値に修正 |
| ABI mismatch | GCC バージョン不一致 | brew reinstall netcdf-fortran |
| WPS URL 404 | GitHub releases にない | archive/refs/tags/ URL を使う |
```

## Claude Code の実行の様子（実際に起きたこと）

プロンプトを貼り付けると、Claude Code はターミナルで各ステップを順番に自律実行し始めました。以下は実際に観察した出来事です。

**jasper API 問題を自動検知してソースを書き換えた**  
`ungrib.exe` のコンパイル中にリンクエラーが発生すると、Claude Code はエラーメッセージを読んで原因を特定し、`dec_jpeg2000.c` と `enc_jpeg2000.c` を jasper 4.x の公開 API に合わせて自動書き換えしました。手動ではかなり手間がかかる作業です。

**netcdf.inc が見つからないエラーを自動解決した**  
`netcdf_combined/include/` に `netcdf.inc` が存在しないことを検知すると、Homebrew のインストールパスから該当ファイルを探し出して手動コピーを実行しました。

**compile.log を読んで成功を確認した**  
コンパイル完了後、`compile.log` の末尾を確認して `wrf.exe`・`real.exe`・`ndown.exe` の3ファイルが正常に生成されているかを自動チェックしました。

**所要時間**  
ダウンロード時間を含めて、全体で **約 60〜90 分** で構築が完了しました。ネットワーク速度や Mac のスペックによって変動しますが、手動でやると半日以上かかることを考えると大幅な時間短縮です。

## 構築後にできること

環境が整ったら、以下のような用途にすぐ使えます。

![](/weather-note/images/cc_fig4_capabilities-1024x517.png)

- **実データシミュレーション**: NCEP FNL データを使った実際の気象イベントの再現計算

- **理想実験**: `em_les`（大渦シミュレーション）や `em_b_wave`（傾圧波）などの教科書的な実験

- **MYNN PBL スキームによる乱流解析**: 乱流運動エネルギー（TKE）や乱流散逸率（EDR）の解析

- **Python によるポスト処理**: `netCDF4` や `cartopy` を使った可視化・解析

## このプロンプトのカスタマイズ方法

プロンプト冒頭の「ユーザー設定」セクションを書き換えることで、様々な環境に対応できます。

- **ドメイン数・解像度・物理スキームの変更**: `namelist.input` の設定値として反映されます

- **「シミュレーション種別」を「理想実験のみ」に変更**: WPS のビルドが不要になるため、jasper 関連のトラブルを完全に回避できます

- **「使用コア数」の変更**: `mpirun -np` の値が自動的に調整されます

また、プロンプト内の **トラブルシューティング表** を事前に読んでおくと、万が一エラーが起きたときに Claude Code の対処を見守りながら理解しやすくなります。

## まとめ

| 項目 | 手動構築 | Claude Code 使用 |
| --- | --- | --- |
| 所要時間 | 半日〜丸1日 | 60〜90分 |
| jasper 4.x 対応 | 手動でソース書き換え | 自動対応 |
| netcdf\_combined 作成 | 手動でファイルコピー | 自動対応 |
| エラー対処 | 自力でログ解析 | 自動検知・修正 |
| 再現性 | 環境依存で低い | プロンプト保存で高い |

**Apple Silicon Mac への WRF 構築は、Claude Code を使うことで大幅に簡略化できます。** 特に jasper 4.x 対応・netcdf\_combined 作成・URL 404 回避といった Mac 固有の問題を自動解決してくれる点は、過去に挫折した経験がある人にとって大きな価値があるでしょう。

プロンプトの内容を自分でも理解しておくことで、Claude Code が対処できなかった場合のデバッグも容易になります。WRF 入門の最初のハードルを下げるツールとして、ぜひ活用してみてください。

## 参考リンク

- [WRF 公式サイト](https://www.mmm.ucar.edu/models/wrf/)

- [WRF GitHub](https://github.com/wrf-model/WRF)

- [Claude Code](https://claude.ai/claude-code)

- [NCEP FNL データ](https://rda.ucar.edu/datasets/ds083.2/)
