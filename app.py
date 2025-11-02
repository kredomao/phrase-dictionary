# app.py
import streamlit as st
import pandas as pd
import sqlite3
from rapidfuzz import process, fuzz
from datetime import datetime
import os
import io

# ---------- 設定 ----------
DB_PATH = "phrases.db"
TABLE = "phrases"
LOG_CSV = "activity_log.csv"  # 操作ログ

# ---------- ユーティリティ ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        context TEXT,
        tags TEXT,
        created_at TEXT,
        usage_count INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def load_all_phrases():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE} ORDER BY usage_count DESC, created_at DESC", conn)
    conn.close()
    return df

def upsert_phrase(source, target, context="", tags=""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    # 簡易：同一 source があれば更新、なければ挿入
    cur.execute(f"SELECT id FROM {TABLE} WHERE source = ?", (source,))
    row = cur.fetchone()
    if row:
        pid = row[0]
        cur.execute(f"UPDATE {TABLE} SET target=?, context=?, tags=? WHERE id=?", (target, context, tags, pid))
    else:
        cur.execute(f"INSERT INTO {TABLE}(source,target,context,tags,created_at) VALUES (?,?,?,?,?)",
                    (source, target, context, tags, now))
    conn.commit()
    conn.close()

def increment_usage(pid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE} SET usage_count = usage_count + 1 WHERE id = ?", (pid,))
    conn.commit()
    conn.close()

def append_log(user, action, details=""):
    """シンプルなCSVログ。後でダウンロードできるようにする。"""
    row = {"timestamp": datetime.utcnow().isoformat(), "user": user, "action": action, "details": details}
    df = pd.DataFrame([row])
    header = not os.path.exists(LOG_CSV)
    df.to_csv(LOG_CSV, mode="a", header=header, index=False, encoding="utf-8")
    
# ---------- 認証 ----------
def load_users_from_secrets():
    """Streamlit Cloud の Secrets に "USERS" キーを入れておくこと
    例: USERS = "alice:pass1,bob:pass2"
    
    ローカル開発時は .streamlit/secrets.toml に以下を追加：
    USERS = "your_username:your_password"
    """
    try:
        raw = st.secrets["USERS"]
    except Exception:
        # Secretsが設定されていない場合はエラー
        st.error("⚠️ ユーザー認証が設定されていません。管理者に連絡してください。")
        st.stop()
        raw = None
    users = {}
    if raw:
        for item in raw.split(","):
            if ":" in item:
                name, pwd = item.split(":", 1)
                users[name.strip()] = pwd.strip()
    return users

def authenticate():
    """ログイン機能"""
    if "logged_in" in st.session_state and st.session_state.logged_in:
        return True
    st.sidebar.title("ログイン")
    users = load_users_from_secrets()
    if not users:
        st.sidebar.error("管理者：まだユーザーが設定されていません（Streamlit Secrets で USERS を指定）。")
        return False
    username = st.sidebar.text_input("ユーザー名")
    password = st.sidebar.text_input("パスワード", type="password")
    if st.sidebar.button("ログイン"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"ようこそ、{username}さん")
            append_log(username, "login", "success")
            st.rerun()
        else:
            st.sidebar.error("認証に失敗しました。ユーザー名とパスワードを確認してください。")
            append_log(username or "unknown", "login_failed", "")
            return False
    return False

# ---------- 初期化 ----------
init_db()
st.set_page_config(page_title="翻訳フレーズ辞書", layout="wide")

# 認証チェック
if not authenticate():
    st.stop()

# ログアウトボタン
st.sidebar.markdown("---")
st.sidebar.write(f"ログイン中: **{st.session_state.user}**")
if st.sidebar.button("ログアウト"):
    append_log(st.session_state.user, "logout", "")
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# メインUI
st.title("翻訳フレーズ辞書（共有版）")
st.write("英語フレーズを保存・検索して、訳をワンクリックで採用できます。")

# 左カラム：インポート / 新規登録
left, right = st.columns([1,2])

with left:
    st.header("データ準備")
    uploaded = st.file_uploader("既存の翻訳CSVをアップロード（source,target,context,tags）", type=["csv"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded, encoding='utf-8-sig')
            # 簡易バリデーション
            if "source" in df.columns and "target" in df.columns:
                count = 0
                for _, r in df.iterrows():
                    target = str(r["target"]).strip()
                    # [要確認]はスキップ
                    if target and target != "[要確認]":
                        upsert_phrase(str(r["source"]).strip(), target,
                                      str(r.get("context","")), str(r.get("tags","")))
                        count += 1
                st.success(f"CSV を DB に取り込みました（{count}件）。")
                append_log(st.session_state.user, "upload_csv", f"rows={count}")
            else:
                st.error("CSVに source と target 列が必要です。")
        except Exception as e:
            st.error(f"CSV 読み込みエラー: {str(e)}")

    st.markdown("---")
    st.header("フレーズ登録（手動）")
    s_src = st.text_input("英語（原文）", key="src_input")
    s_tgt = st.text_input("日本語（訳）", key="tgt_input")
    s_ctx = st.text_input("コンテキスト（例：キャラ名）", key="ctx_input")
    s_tags = st.text_input("タグ（カンマ区切り）", key="tags_input")
    if st.button("登録／更新"):
        if s_src.strip() and s_tgt.strip():
            upsert_phrase(s_src.strip(), s_tgt.strip(), s_ctx.strip(), s_tags.strip())
            st.success("登録しました。検索から確認できます。")
            append_log(st.session_state.user, "manual_upsert", f"{s_src} -> {s_tgt}")
        else:
            st.error("原文と訳は必須です。")

    st.markdown("---")
    if st.button("辞書をCSVでエクスポート"):
        df_all = load_all_phrases()
        csv = df_all.to_csv(index=False, encoding="utf-8-sig")
        b = csv.encode("utf-8-sig")
        st.download_button("CSVをダウンロード", data=b, file_name="phrases_export.csv", mime="text/csv")
        append_log(st.session_state.user, "export_csv", f"rows={len(df_all)}")

# 右カラム：検索・候補表示
with right:
    st.header("検索と候補提示")
    query = st.text_input("検索／候補を出したい英語フレーズを入力", placeholder="例: Let's go!", key="query")
    limit = st.slider("候補上限数", 1, 10, 5)
    if query:
        df_all = load_all_phrases()
        choices = df_all["source"].tolist()
        if len(choices) == 0:
            st.info("辞書が空です。左でCSVをアップロードするか手で登録してください。")
        else:
            results = process.extract(query, choices, scorer=fuzz.token_sort_ratio, limit=limit)
            # results: [(match, score, idx), ...]
            st.write("候補（上からスコア順）:")
            for match, score, _ in results:
                row = df_all[df_all["source"] == match].iloc[0]
                col1, col2, col3 = st.columns([4,4,1])
                with col1:
                    st.markdown(f"**原文**: `{row['source']}`")
                    st.markdown(f"**訳**: {row['target']}")
                    st.markdown(f"**context**: {row.get('context','')}")
                with col2:
                    st.markdown(f"スコア: {score}")
                with col3:
                    if st.button("採用", key=f"adopt_{int(row['id'])}"):
                        # 採用した訳をエディタ用に反映（session_state）
                        st.session_state["selected_target"] = row['target']
                        increment_usage(int(row['id']))
                        append_log(st.session_state.user, "adopt", f"src={row['source'][:50]},id={row['id']}")
                        st.success("採用しました（編集欄に反映されます）。")
            st.markdown("---")
            st.write("訳を編集して新規保存することもできます。")
            tgt_edit = st.text_area("編集（最終的に使う訳）", value=st.session_state.get("selected_target",""), height=120)
            new_ctx = st.text_input("（任意）この訳のコンテキスト")
            if st.button("この訳を辞書に保存"):
                src_norm = query.strip()
                if src_norm and tgt_edit.strip():
                    upsert_phrase(src_norm, tgt_edit.strip(), new_ctx.strip(), "")
                    append_log(st.session_state.user, "save_translation", f"{src_norm[:50]} -> {tgt_edit.strip()[:50]}")
                    st.success("辞書に保存しました。")
                else:
                    st.error("原文と訳が必要です。")

    st.markdown("## 辞書一覧（確認）")
    if st.button("一覧更新"):
        pass
    df_show = load_all_phrases()
    st.dataframe(df_show)

st.markdown("---")
st.caption("使い方: 左でCSVを読み込む／手で登録 → 右で原文を入力して候補を見つける → 採用ボタンで訳を反映 → 必要に応じて編集して辞書へ保存")

# ログのダウンロード（管理者向け）
st.sidebar.markdown("---")
st.sidebar.header("管理")
if st.sidebar.button("操作ログをダウンロード（CSV）"):
    if os.path.exists(LOG_CSV):
        with open(LOG_CSV, "rb") as f:
            data = f.read()
        st.sidebar.download_button("ログをダウンロード", data=data, file_name=LOG_CSV, mime="text/csv")
        append_log(st.session_state.user, "download_log", "")
    else:
        st.sidebar.info("まだログがありません。")

