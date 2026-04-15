# Weather Note — よく使うコマンド集
# 使い方: make <コマンド名>

.PHONY: new preview publish help

## 新しい記事を作成する
## 使い方: make new SLUG=20260416-記事名
new:
	@if [ -z "$(SLUG)" ]; then \
		echo "❌ スラグを指定してください。例: make new SLUG=20260416-my-post"; \
		exit 1; \
	fi
	hugo new content/posts/$(SLUG).md
	@echo ""
	@echo "✅ content/posts/$(SLUG).md を作成しました"
	@echo "   タイトル・本文を編集してから make publish を実行してください"

## ローカルでプレビューする
preview:
	@echo "🌐 http://localhost:1313/weather-note/ でプレビュー中..."
	@echo "   終了するには Ctrl+C"
	hugo server

## GitHubに公開する
## 使い方: make publish MSG="記事タイトルや変更内容"
publish:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ コミットメッセージを指定してください。例: make publish MSG=\"新記事: タイトル\""; \
		exit 1; \
	fi
	git add -A
	git commit -m "$(MSG)"
	git push
	@echo ""
	@echo "✅ 公開完了！1〜2分後に反映されます"
	@echo "   https://weathernote.github.io/weather-note/"

## ヘルプを表示する
help:
	@echo "使えるコマンド:"
	@echo ""
	@echo "  make new SLUG=20260416-記事名    新しい記事ファイルを作成"
	@echo "  make preview                      ローカルでプレビュー"
	@echo "  make publish MSG=\"コミットメッセージ\"  GitHubに公開"
