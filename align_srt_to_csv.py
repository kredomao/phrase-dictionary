# align_srt_to_csv.py
# 必要: pip install srt pandas
import srt
from datetime import timedelta
import pandas as pd
import sys
import os

ENG_SRT = "english.srt"
JPN_SRT = "japanese.srt"
OUT_CSV = "pairs.csv"
MIN_OVERLAP = timedelta(milliseconds=100)  # 重なりとみなす最小時間

def load_subs(path):
    if not os.path.exists(path):
        print(f"ファイルが見つかりません: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    try:
        return list(srt.parse(txt))
    except Exception as e:
        print("SRTの読み取りに失敗しました:", e)
        sys.exit(1)

def overlap(a_start, a_end, b_start, b_end):
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return (earliest_end - latest_start) >= MIN_OVERLAP

def normalize_text(t: str) -> str:
    # 改行をスペースに、前後の空白を削る
    return " ".join(t.replace("\r","").split())

def main():
    eng = load_subs(ENG_SRT)
    jpn = load_subs(JPN_SRT)

    pairs = []
    j_idx = 0
    for e in eng:
        matched_texts = []
        matched_j_indices = []
        # jpn を先頭から順に探す（効率化のため逐次）
        for k in range(j_idx, len(jpn)):
            j = jpn[k]
            if overlap(e.start, e.end, j.start, j.end):
                matched_texts.append(normalize_text(j.content))
                matched_j_indices.append(k)
            # もし日本語の字幕開始時間が英語の終了時間より大きく離れていたら次へ
            if j.start > e.end + timedelta(seconds=2):
                break

        if matched_texts:
            target = " ".join(matched_texts)
            pairs.append({
                "source": normalize_text(e.content),
                "target": target,
                "eng_start": str(e.start),
                "eng_end": str(e.end),
                "jpn_start": str(jpn[matched_j_indices[0]].start),
                "jpn_end": str(jpn[matched_j_indices[-1]].end)
            })
            # 次は最後に使った日本語の次のインデックスから開始
            j_idx = matched_j_indices[-1] + 1
        else:
            pairs.append({
                "source": normalize_text(e.content),
                "target": "",
                "eng_start": str(e.start),
                "eng_end": str(e.end),
                "jpn_start": "",
                "jpn_end": ""
            })

    df = pd.DataFrame(pairs, columns=["source","target","eng_start","eng_end","jpn_start","jpn_end"])
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"生成しました: {OUT_CSV} （行数: {len(df)})")
    
    # 統計情報を表示
    matched = df[df["target"] != ""].shape[0]
    unmatched = df[df["target"] == ""].shape[0]
    print(f"マッチした行: {matched}")
    print(f"マッチしなかった行: {unmatched}")
    print(f"マッチ率: {matched/(matched+unmatched)*100:.1f}%")

if __name__ == "__main__":
    main()

