# merge_dictionaries.py
# 複数の辞書CSVを統合して重複を削除

import pandas as pd
import sys

def merge_csv_files(input_files, output_file):
    """複数のCSVファイルを統合"""
    all_data = []
    
    print("=" * 60)
    print("辞書統合ツール")
    print("=" * 60)
    print()
    
    # 各ファイルを読み込む
    for file in input_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig')
            print(f"[OK] {file} を読み込みました（{len(df)}行）")
            all_data.append(df)
        except Exception as e:
            print(f"[ERROR] {file} の読み込みに失敗: {e}")
    
    if not all_data:
        print("[ERROR] 読み込めるファイルがありませんでした")
        return False
    
    # 統合
    merged = pd.concat(all_data, ignore_index=True)
    print(f"\n統合前の総フレーズ数: {len(merged)}")
    
    # source列で重複を削除（最初に出現したものを保持）
    before_count = len(merged)
    merged_unique = merged.drop_duplicates(subset=['source'], keep='first')
    after_count = len(merged_unique)
    duplicates = before_count - after_count
    
    print(f"重複削除後: {after_count}")
    print(f"削除された重複: {duplicates}")
    
    # 必要な列のみを保持
    if 'source' in merged_unique.columns and 'target' in merged_unique.columns:
        # context と tags 列も保持（存在する場合）
        columns_to_keep = ['source', 'target']
        if 'context' in merged_unique.columns:
            columns_to_keep.append('context')
        if 'tags' in merged_unique.columns:
            columns_to_keep.append('tags')
        
        final_df = merged_unique[columns_to_keep].copy()
    else:
        final_df = merged_unique
    
    # 保存
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 60)
    print("[完成しました！]")
    print("=" * 60)
    print(f"出力ファイル: {output_file}")
    print(f"最終フレーズ数: {len(final_df)}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    # 統合するファイルのリスト
    input_files = [
        "BiKenS6E6_dictionary.csv",
        "BiKen5_3_Mech_dictionary.csv",
        "BiKenS1E4_Beach_dictionary.csv"
    ]
    
    output_file = "complete_dictionary.csv"
    
    merge_csv_files(input_files, output_file)

