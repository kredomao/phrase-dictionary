# import_to_db.py
# CSVファイルを直接データベースに取り込むスクリプト

import sqlite3
import pandas as pd
from datetime import datetime
import sys

DB_PATH = "phrases.db"
TABLE = "phrases"

def init_db():
    """データベースを初期化"""
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
    print("[OK] データベースを初期化しました")

def import_csv(csv_path):
    """CSVファイルをデータベースに取り込む"""
    try:
        # CSVを読み込み
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"[OK] {csv_path} を読み込みました（{len(df)}行）")
        
        # 必要な列があるか確認
        if "source" not in df.columns or "target" not in df.columns:
            print("[ERROR] CSVに source と target 列が必要です")
            return False
        
        # データベースに接続
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        imported = 0
        updated = 0
        skipped = 0
        
        for idx, row in df.iterrows():
            source = str(row["source"]).strip()
            target = str(row["target"]).strip()
            
            # [要確認]の行はスキップ
            if target == "[要確認]" or target == "":
                skipped += 1
                continue
            
            context = str(row.get("context", "")).strip()
            tags = str(row.get("tags", "")).strip()
            
            # 既存のレコードを確認
            cur.execute(f"SELECT id FROM {TABLE} WHERE source = ?", (source,))
            existing = cur.fetchone()
            
            if existing:
                # 更新
                cur.execute(f"""
                    UPDATE {TABLE} 
                    SET target=?, context=?, tags=? 
                    WHERE id=?
                """, (target, context, tags, existing[0]))
                updated += 1
            else:
                # 新規挿入
                cur.execute(f"""
                    INSERT INTO {TABLE}(source, target, context, tags, created_at) 
                    VALUES (?,?,?,?,?)
                """, (source, target, context, tags, now))
                imported += 1
            
            # 進捗表示（100件ごと）
            if (idx + 1) % 100 == 0:
                print(f"処理中... {idx + 1}/{len(df)}")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("[完了しました！]")
        print("=" * 60)
        print(f"新規追加: {imported}件")
        print(f"更新: {updated}件")
        print(f"スキップ: {skipped}件")
        print(f"合計: {imported + updated}件のフレーズが辞書に登録されました")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] エラーが発生しました: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("使い方: python import_to_db.py <CSVファイル>")
        print("例: python import_to_db.py BiKenS6E6_dictionary.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    print("=" * 60)
    print("CSV -> データベース 直接取り込みツール")
    print("=" * 60)
    
    init_db()
    success = import_csv(csv_path)
    
    if success:
        print("\n次のステップ:")
        print("  1. Streamlitアプリを起動: streamlit run app.py")
        print("  2. ブラウザで http://localhost:8501 を開く")
        print("  3. 右側の検索欄で英語フレーズを検索してみてください！")

if __name__ == "__main__":
    main()

