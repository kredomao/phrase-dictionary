# クイックスタートガイド

## ローカルで試す（5分）

### 1. パッケージをインストール

```bash
pip install -r requirements.txt
```

### 2. アプリを起動

```bash
streamlit run app.py
```

ブラウザで `http://127.0.0.1:8501` を開く

### 3. ログイン

**デフォルトのログイン情報**（ローカル開発用）:
- ユーザー名: `admin`
- パスワード: `password123`

⚠️ **本番環境では必ずStreamlit Secretsで変更してください**

### 4. 辞書をインポート

既にSRTから生成した辞書がある場合：

1. 左側の「既存の翻訳CSVをアップロード」をクリック
2. `BiKenS6E6_dictionary.csv` などを選択
3. 自動的にデータベースに取り込まれます

### 5. 検索してみる

1. 右側の検索欄に英語フレーズを入力（例: `Hello`）
2. 類似候補が表示されます
3. 「採用」ボタンで訳を編集欄に反映
4. 必要に応じて編集して「この訳を辞書に保存」

## HeyGenのSRTから辞書を作成

### 方法1: スクリプトを使う

```bash
python create_dictionary.py "english.srt" "japanese.srt" "output.csv"
```

### 方法2: 直接DBに取り込む

```bash
python import_to_db.py "pairs.csv"
```

生成されたCSVをアプリでアップロードすれば使えます。

## パートナーと共有する

詳しくは [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) を参照してください。

簡単な手順：

1. GitHubにプッシュ
2. Streamlit Cloudでデプロイ
3. Secretsでユーザー設定
4. URLを共有

## よくある質問

### Q: データベースはどこに保存される？

A: `phrases.db` というSQLiteファイルに保存されます。ローカルでは永続化されますが、Streamlit Cloudでは一時的です。定期的にCSVエクスポートでバックアップを取ってください。

### Q: 複数人で同時に使える？

A: はい。ただし、Streamlit Cloudの無料プランでは同時接続数に制限があります。また、SQLiteは同時書き込みに弱いので、大規模な運用ではPostgreSQLへの移行を推奨します。

### Q: パスワードを忘れた

A: 管理者がStreamlit CloudのSecretsを更新する必要があります。

### Q: ログはどこで見られる？

A: サイドバーの「管理」→「操作ログをダウンロード（CSV）」でダウンロードできます。

## トラブルシューティング

### アプリが起動しない

```bash
# パッケージを再インストール
pip install --upgrade -r requirements.txt

# Python バージョン確認（3.9以上が必要）
python --version
```

### 文字化けする

- CSVはUTF-8（BOM付き）で保存してください
- Excelで開く場合はインポート機能を使用

### データが消えた

- Streamlit Cloudでは定期的にファイルシステムがリセットされます
- バックアップからCSVをアップロードして復元してください

## サポート

問題が発生した場合は、以下を確認：

1. エラーメッセージのスクリーンショット
2. 何をしようとしたか
3. 使用環境（ローカル or Streamlit Cloud）

これらの情報があれば、迅速にサポートできます！

