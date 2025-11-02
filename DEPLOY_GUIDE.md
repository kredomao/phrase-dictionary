# Streamlit Cloud デプロイガイド

このガイドでは、翻訳フレーズ辞書アプリをStreamlit Cloudに公開する手順を説明します。

## 📋 準備するもの

- GitHubアカウント
- このプロジェクトのファイル一式

## 🚀 デプロイ手順

### ステップ1: GitHubリポジトリを作成

1. [GitHub](https://github.com)にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例: `phrase-dictionary`）
4. 「Public」または「Private」を選択（どちらでもOK）
5. 「Create repository」をクリック

### ステップ2: ローカルファイルをGitHubにプッシュ

PowerShellまたはコマンドプロンプトで以下を実行：

```powershell
# プロジェクトフォルダに移動
cd "C:\Users\kinta\Desktop\Original translation"

# Gitリポジトリを初期化
git init

# すべてのファイルをステージング
git add .

# コミット
git commit -m "Initial commit - phrase dictionary app"

# メインブランチにリネーム
git branch -M main

# リモートリポジトリを追加（<あなたのユーザー名>と<リポジトリ名>を置き換え）
git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git

# プッシュ
git push -u origin main
```

**注意**: 初回プッシュ時にGitHubのユーザー名とパスワード（またはPersonal Access Token）を求められる場合があります。

### ステップ3: Streamlit Cloudでデプロイ

1. [https://share.streamlit.io](https://share.streamlit.io) にアクセス
2. GitHubアカウントでログイン
3. 「New app」ボタンをクリック
4. 以下を選択：
   - **Repository**: 作成したリポジトリ（例: `phrase-dictionary`）
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. 「Deploy!」をクリック

数分で自動的にデプロイされます。

### ステップ4: Secrets（ユーザー認証情報）を設定

1. Streamlit Cloudのアプリダッシュボードで、デプロイしたアプリを選択
2. 右側の「⋮」メニュー → 「Settings」をクリック
3. 左メニューから「Secrets」を選択
4. 以下のフォーマットでユーザー情報を入力：

```toml
USERS = "alice:password123,bob:secretpass,yourname:yourpass"
```

**フォーマット**: `ユーザー名:パスワード` をカンマで区切る

5. 「Save」をクリック

**重要**: パスワードは推測されにくいものを使用してください。

### ステップ5: アプリのURLを共有

デプロイが完了すると、以下のようなURLが発行されます：

```
https://your-app-name.streamlit.app
```

このURLをパートナーに共有すれば、誰でもアクセスできます。

## 🔐 セキュリティのベストプラクティス

1. **強力なパスワード**: 少なくとも8文字以上、英数字と記号を組み合わせる
2. **定期的な変更**: 3〜6ヶ月ごとにパスワードを変更
3. **HTTPSを確認**: Streamlit CloudはデフォルトでHTTPSを使用（安全）
4. **ログの監視**: 定期的に操作ログをダウンロードして不審なアクティビティをチェック

## 📊 操作ログについて

アプリは以下の操作をログに記録します：

- ログイン/ログアウト
- CSVアップロード
- フレーズの採用
- 辞書への保存
- エクスポート

**重要**: Streamlit Cloudのファイルシステムは一時的なので、定期的にログをダウンロードしてください。

ログのダウンロード方法：
1. アプリにログイン
2. サイドバーの「管理」セクション
3. 「操作ログをダウンロード（CSV）」ボタンをクリック

## 🔄 アプリの更新方法

コードを更新した場合：

```powershell
# 変更をコミット
git add .
git commit -m "Update: 機能追加の説明"

# プッシュ
git push
```

Streamlit Cloudが自動的に再デプロイします（数分かかります）。

## 🆘 トラブルシューティング

### デプロイが失敗する

- `requirements.txt` のパッケージを確認
- GitHubのリポジトリが正しくプッシュされているか確認
- Streamlit Cloudのログを確認（アプリページの「Manage app」→「Logs」）

### ログインできない

- Secrets の `USERS` が正しく設定されているか確認
- フォーマットが `username:password,username2:password2` になっているか確認
- Secretsを更新したら、アプリを再起動（「⋮」→「Reboot app」）

### データベースが空になる

- Streamlit Cloudでは、デプロイごとにファイルシステムがリセットされます
- 定期的にCSVエクスポートでバックアップを取る
- 初回デプロイ後、CSVをアップロードして辞書を復元

## 📝 パートナーへの使い方説明

パートナーに以下を伝えてください：

1. **アプリURL**: `https://your-app-name.streamlit.app`
2. **ユーザー名とパスワード**: Secretsで設定したもの
3. **基本的な使い方**:
   - サイドバーでログイン
   - 左側でCSVをアップロード（初回のみ）
   - 右側で英語フレーズを検索
   - 「採用」ボタンで訳を選択
   - 必要に応じて編集して保存
4. **バックアップ**: 作業後は「辞書をCSVでエクスポート」でバックアップを取る習慣をつけてもらう

## 🎓 次のステップ

より高度な機能が必要な場合：

1. **Google Sheetsとの連携**: ログと辞書を自動的にGoogle Sheetsに保存
2. **メール通知**: 重要な操作（大量削除など）があった時に通知
3. **バージョン管理**: 辞書の変更履歴を追跡
4. **HeyGen API連携**: 翻訳したSRTを自動アップロード

必要であれば、追加実装をサポートします！

