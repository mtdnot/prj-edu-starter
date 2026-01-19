# prj-EDU starter: 「わかりやすい地震予知学」(Jupyter Book + GitHub Pages + n8n)

このテンプレは、**あなたの作業を「記事を書く→GitHubにpush」だけ**に寄せて、

- Webサイト(Jupyter Book)の自動ビルド＆公開(GitHub Pages)
- 新規/更新記事の一覧(JSONフィード)の自動生成
- n8n側で、そのフィードを監視して **X投稿/YouTube台本生成/予約投稿** を自動化

までを“繋ぐ”前提で作ったスターターです。

## 0. 先に結論（あなたがやる作業は3つだけ）

1. GitHubにこのフォルダをそのままリポジトリとして置く
2. `content/` にMyST Markdownで記事を追加/編集してpush
3. (最初の1回だけ) GitHub Pagesとn8nの設定をする

以降は、**pushするたびにWebが更新**され、`/social/latest.json` が更新されます。

n8nは `latest.json` を定期ポーリングして、新しい記事を見つけたら自動で投稿案を作り、予約投稿します。

## 1. ディレクトリ構成

- `_config.yml` : Jupyter Book 設定
- `_toc.yml` : 目次（記事追加時に追記）
- `intro.md` : トップ
- `content/` : 記事置き場（MyST Markdown）
- `tools/build_latest_json.py` : 新規/更新記事フィードを生成
- `.github/workflows/deploy.yml` : ビルド＆GitHub Pagesデプロイ

## 2. 記事テンプレ（必須メタデータ）

`content/*.md` の先頭に YAML front matter を置きます。

例：

```yaml
---
title: "地震予知はできるの？できないの？（L0→L3）"
date: 2026-01-18
slug: earthquake-what-we-can-know
summary: "『当てる魔法』ではないが、観測と統計で分かることはある。レイヤー別に整理。"
tags: ["overview","gnss","ionosphere"]
status: published
---
```

- `status: published` の記事だけがフィードに載ります。
- `slug` がURLの一部になります。

## 3. GitHub Pages 公開

- GitHubのリポジトリ設定 → Pages
- Build and deployment: GitHub Actions を選択

Workflowは `.github/workflows/deploy.yml` が担います。

> このテンプレは **Sphinx-based Jupyter Book v1** 想定です。
> そのため GitHub Actions では `jupyter-book<2` をインストールしています。

## 4. n8n側（概要）

n8nは次の2ワークフローを作るのが最短です。

### (A) Ingest: latest.json を監視して「投稿キュー」を作る

- Trigger: Schedule（例：1時間ごと）
- HTTP Request: `https://<your-gh-pages-domain>/social/latest.json`
- Code: まだ処理していない `slug` だけ抽出（Data StoreやGoogle Sheetsで重複排除）
- AI: 記事の `summary` と本文冒頭を使って
  - X投稿（短文）
  - Xスレッド（3〜6投稿）
  - YouTube Shorts台本（~60秒）
  - タイトル案
  を生成
- Store: キューに保存（Google Sheets/Airtable/Notionなど）

### (B) Post: キューから予約時間になったらXに投稿

- Trigger: Schedule（例：1日3回）
- Read queue: 今日の未投稿を取得
- Safety gate: 禁止語や断定表現がないかチェック
- X node で投稿

YouTubeまで完全自動化したい場合は、(C) として「台本→音声→動画→アップロード」を追加します。

注意：YouTubeアップロードは n8n Cloud だとGoogle側制約で弾かれるケースがあり、**自己ホストn8n**が推奨されます。

