import cv2
import os
import re
import argparse
from tqdm import tqdm

def natural_sort_key(s):
    """
    自然な順序でソートするためのキー関数
    数字を含む文字列を正しく並べ替えます
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

def create_video_from_images(folder_path, output_path, file_pattern="*.jpeg", fps=30):
    """
    指定フォルダの画像から動画を作成する関数

    Args:
        folder_path (str): 画像が格納されているフォルダのパス
        output_path (str): 出力する動画ファイルのパス
        file_pattern (str, optional): 対象とする画像のパターン。デフォルトは*.jpeg
        fps (int, optional): 動画のフレームレート。デフォルトは30

    Returns:
        bool: 動画作成に成功したかどうか
    """
    # 画像ファイルを取得（パターンマッチング）
    images = [img for img in os.listdir(folder_path) if img.endswith(file_pattern.replace("*", ""))]
    
    # 自然な順序でソート
    images.sort(key=natural_sort_key)

    if not images:
        print(f"No matching images found in the folder with pattern: {file_pattern}")
        return False

    # 最初のフレームから動画のサイズを取得
    first_image_path = os.path.join(folder_path, images[0])
    frame = cv2.imread(first_image_path)
    
    if frame is None:
        print(f"Could not read the first image: {first_image_path}")
        return False

    height, width, layers = frame.shape

    # VideoWriterの設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    dots = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    # 進行状況バーの設定
    with tqdm(total=len(images), desc="画像から動画を作成中", unit="frame") as pbar:
        # 画像を動画に書き込み
        for image in images:
            img_path = os.path.join(folder_path, image)
            frame = cv2.imread(img_path)
            
            if frame is None:
                print(f"Skipping problematic image: {img_path}")
                pbar.update(1)
                continue
            
            video.write(frame)
            i = (i + 1) % len(dots)
            pbar.set_description(f"画像から動画を作成中 {dots[i]}")
            pbar.update(1)

    video.release()
    print(f"動画が正常に作成されました: {output_path}")
    return True

def parse_arguments():
    """
    コマンドライン引数を解析する関数
    """
    parser = argparse.ArgumentParser(description="画像から動画を作成するスクリプト")
    parser.add_argument("-f", "--folder", 
                        default=r"C:\Users\nayuta\Documents\aaaaa", 
                        help="画像が格納されているフォルダのパス")
    parser.add_argument("-o", "--output", 
                        help="出力する動画ファイルのパス (指定しない場合は入力フォルダに作成)")
    parser.add_argument("-p", "--pattern", 
                        default="*.jpeg", 
                        help="対象とする画像のパターン (デフォルト: *.jpeg)")
    parser.add_argument("--fps", 
                        type=int, 
                        default=1, 
                        help="動画のフレームレート (デフォルト: 1)")
    
    return parser.parse_args()

def main():
    # コマンドライン引数の解析
    args = parse_arguments()

    # 出力パスが指定されていない場合は、入力フォルダに動画ファイルを作成
    if not args.output:
        output_path = os.path.join(args.folder, "output_video.mp4")
    else:
        output_path = args.output

    # 動画作成
    success = create_video_from_images(
        args.folder, 
        output_path, 
        file_pattern=args.pattern,
        fps=args.fps
    )

    if not success:
        print("動画の作成に失敗しました。")

if __name__ == '__main__':
    main()
