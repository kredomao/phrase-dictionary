# create_dictionary.py
# HeyGenのSRTファイルから翻訳辞書CSVを自動生成
# 使い方: python create_dictionary.py <英語SRT> <日本語SRT> [出力CSV]

import srt
from datetime import timedelta
import pandas as pd
import sys
import os

MIN_OVERLAP = timedelta(milliseconds=100)  # 重なりとみなす最小時間

def load_subs(path):
    """SRTファイルを読み込む"""
    if not os.path.exists(path):
        print(f"[ERROR] ファイルが見つかりません: {path}")
        sys.exit(1)
    
    # BOM付きUTF-8、UTF-8、Shift-JIS、CP932を試す
    encodings = ['utf-8-sig', 'utf-8', 'shift_jis', 'cp932']
    
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                txt = f.read()
            subs = list(srt.parse(txt))
            print(f"[OK] {path} を読み込みました（{len(subs)}セグメント, {encoding}）")
            return subs
        except (UnicodeDecodeError, Exception):
            continue
    
    print(f"[ERROR] {path} の読み取りに失敗しました")
    sys.exit(1)

def overlap(a_start, a_end, b_start, b_end):
    """2つの時間範囲が重なっているかチェック"""
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return (earliest_end - latest_start) >= MIN_OVERLAP

def normalize_text(t: str) -> str:
    """テキストを正規化（改行をスペースに、前後の空白を削除）"""
    return " ".join(t.replace("\r","").split())

def align_subs(eng_subs, jpn_subs):
    """英語と日本語の字幕を時間で突合"""
    pairs = []
    j_idx = 0
    matched_count = 0
    
    for i, e in enumerate(eng_subs):
        matched_texts = []
        matched_j_indices = []
        
        # 日本語字幕を探す
        for k in range(j_idx, len(jpn_subs)):
            j = jpn_subs[k]
            if overlap(e.start, e.end, j.start, j.end):
                matched_texts.append(normalize_text(j.content))
                matched_j_indices.append(k)
            # 日本語の開始時間が英語の終了時間より大きく離れていたらスキップ
            if j.start > e.end + timedelta(seconds=2):
                break
        
        source_text = normalize_text(e.content)
        
        if matched_texts:
            target_text = " ".join(matched_texts)
            pairs.append({
                "source": source_text,
                "target": target_text,
                "context": f"Time: {e.start}",
                "tags": "",
                "eng_start": str(e.start),
                "eng_end": str(e.end),
                "jpn_start": str(jpn_subs[matched_j_indices[0]].start) if matched_j_indices else "",
                "jpn_end": str(jpn_subs[matched_j_indices[-1]].end) if matched_j_indices else ""
            })
            matched_count += 1
            # 次は最後に使った日本語の次から
            if matched_j_indices:
                j_idx = matched_j_indices[-1] + 1
        else:
            # マッチしなかった場合も記録（後で手動確認用）
            pairs.append({
                "source": source_text,
                "target": "[要確認]",
                "context": f"Time: {e.start} (マッチなし)",
                "tags": "unmatched",
                "eng_start": str(e.start),
                "eng_end": str(e.end),
                "jpn_start": "",
                "jpn_end": ""
            })
        
        # 進捗表示（10%ごと）
        if (i + 1) % max(1, len(eng_subs) // 10) == 0:
            progress = (i + 1) / len(eng_subs) * 100
            print(f"処理中... {progress:.0f}%")
    
    return pairs, matched_count

def main():
    # コマンドライン引数を取得
    if len(sys.argv) < 3:
        print("使い方: python create_dictionary.py <英語SRT> <日本語SRT> [出力CSV]")
        print("例: python create_dictionary.py english.srt japanese.srt pairs.csv")
        sys.exit(1)
    
    eng_path = sys.argv[1]
    jpn_path = sys.argv[2]
    out_csv = sys.argv[3] if len(sys.argv) > 3 else "pairs.csv"
    
    print("=" * 60)
    print("HeyGen SRT -> 翻訳辞書 変換ツール")
    print("=" * 60)
    
    # SRTファイルを読み込み
    eng_subs = load_subs(eng_path)
    jpn_subs = load_subs(jpn_path)
    
    print(f"\n字幕を突合しています...")
    pairs, matched_count = align_subs(eng_subs, jpn_subs)
    
    # DataFrameを作成してCSVに保存
    df = pd.DataFrame(pairs)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")  # Excel対応のためBOM付き
    
    # 統計情報を表示
    total = len(pairs)
    unmatched = total - matched_count
    match_rate = (matched_count / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("[完成しました！]")
    print("=" * 60)
    print(f"出力ファイル: {out_csv}")
    print(f"総フレーズ数: {total}")
    print(f"マッチ成功: {matched_count} ({match_rate:.1f}%)")
    print(f"要確認: {unmatched} ({100-match_rate:.1f}%)")
    
    if unmatched > 0:
        print(f"\nヒント: '{out_csv}' 内の [要確認] マークがついたフレーズは")
        print(f"   タイミングがずれている可能性があります。手動で確認してください。")
    
    print(f"\n次のステップ:")
    print(f"   1. 'streamlit run app.py' でアプリを起動")
    print(f"   2. 左側で '{out_csv}' をアップロード")
    print(f"   3. 辞書として使えるようになります！")
    print("=" * 60)

if __name__ == "__main__":
    main()

