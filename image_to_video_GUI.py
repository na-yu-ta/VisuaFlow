import os
import re
import sys
import cv2
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tqdm import tqdm
import threading

def natural_sort_key(s):
    """
    自然な順序でソートするためのキー関数
    数字を含む文字列を正しく並べ替えます
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

class ImageToVideoConverter:
    def __init__(self, master):
        self.master = master
        master.title("VisuaFlow")
        master.geometry("450x500")
        
        # 画像フォルダ選択
        self.folder_label = tk.Label(master, text="画像フォルダ")
        self.folder_label.pack(pady=10)
        
        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(master, textvariable=self.folder_path, width=50, state='readonly')
        self.folder_entry.pack(pady=5)
        
        self.browse_button = tk.Button(master, text="フォルダ選択", command=self.browse_folder)
        self.browse_button.pack(pady=5)
        
        # 出力ファイル名
        self.output_label = tk.Label(master, text="出力ファイル名")
        self.output_label.pack(pady=10)
        
        self.output_name = tk.StringVar(value="{day}-{hour}-{min}-{sec}")
        self.output_entry = tk.Entry(master, textvariable=self.output_name, width=50)
        self.output_entry.pack(pady=5)
        
        # 画像パターン
        self.pattern_label = tk.Label(master, text="画像パターン")
        self.pattern_label.pack(pady=10)
        
        self.pattern_options = [
            "*.jpg", "*.jpeg",   # JPEG形式
            "*.png",             # PNG形式
            "*.bmp",             # ビットマップ形式
            "*.tiff", "*.tif",   # TIFF形式
            "*.webp",            # WebP形式
            "*.gif",             # GIF形式
            "*.heic",            # iPhone画像形式
            "*.avif"             # 新しい高圧縮形式
        ]
        self.pattern = tk.StringVar(value=self.pattern_options[0])
        self.pattern_dropdown = ttk.Combobox(master, textvariable=self.pattern, values=self.pattern_options, state="readonly", width=47)
        self.pattern_dropdown.pack(pady=5)
        
        # FPS
        self.fps_label = tk.Label(master, text="フレームレート")
        self.fps_label.pack(pady=10)
        
        self.fps = tk.IntVar(value=30)
        self.fps_spinbox = tk.Spinbox(master, from_=1, to=240, textvariable=self.fps, width=10)
        self.fps_spinbox.pack(pady=5)
        
        # 変換ボタン
        self.convert_button = tk.Button(master, text="動画に変換", command=self.start_conversion)
        self.convert_button.pack(pady=20)
        
        # 進行状況バー
        self.progress = ttk.Progressbar(master, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        # ステータスラベル
        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

    def browse_folder(self):
        """フォルダ選択ダイアログを開く"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def start_conversion(self):
        """変換処理をスレッドで実行"""
        # 入力チェック
        if not self.folder_path.get():
            messagebox.showerror("エラー", "画像フォルダを選択してください")
            with open("log.txt", "a") as f:
                f.write("Failed to select image folder\n")
            return

        # ボタンを無効化
        self.convert_button.config(state=tk.DISABLED)
        self.status_label.config(text="変換中...")
        
        # スレッドで変換処理を実行
        thread = threading.Thread(target=self.convert_images_to_video)
        thread.start()

    def convert_images_to_video(self):
        """画像から動画への変換処理"""
        try:
            with open("log.txt", "a") as f:
                f.write("Conversion started at " + str(datetime.datetime.now()) + "\n")
            # 入力パラメータ取得
            folder_path = self.folder_path.get()
            output_name = self.output_name.get()
            output_name = output_name.replace("{day}", str(datetime.date.today()))
            output_name = output_name.replace("{hour}", str(datetime.datetime.now().hour))
            output_name = output_name.replace("{min}", str(datetime.datetime.now().minute))
            output_name = output_name.replace("{sec}", str(datetime.datetime.now().second))
            output_name = output_name + ".mp4"

            # output_nameがファイル名として使用可能であるか調べる
            if not re.match(r"[^\/\:\*?\?""]+", output_name):
                with open("log.txt", "a") as f:
                    f.write("Failed to generate output name\n")
                messagebox.showerror("警告", f"{output_name}はファイル名として使用できませんXDXDXD\n勝手に設定しますね!!!!!")
                output_name = f"{datetime.date.today()}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.mp4"
            # output_nameがかぶっているか調べる
            if os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), "output", output_name)):
                with open("log.txt", "a") as f:
                    f.write("Failed to generate output name\n")
                messagebox.showerror("警告", f"{output_name}はファイル名として使用できませんXDXDXD\n勝手に設定しますね!!!!!")
                output_name = f"{datetime.date.today()}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.mp4"
            
            # outputフォルダを作成
            output_dir = os.path.join(os.path.dirname(sys.argv[0]), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, output_name)
            file_pattern = self.pattern.get()
            fps = self.fps.get()

            # 画像ファイルを取得（パターンマッチング）
            images = [img for img in os.listdir(folder_path) if img.endswith(file_pattern.replace("*", ""))]
            
            # 自然な順序でソート
            images.sort(key=natural_sort_key)

            if not images:
                with open("log.txt", "a") as f:
                    f.write("Failed to find images\n")
                messagebox.showerror("エラー", f"画像が見つかりませんでしたXDXDXD\nパターン: {file_pattern}は存在してますか？？？")
                self.master.after(0, self.show_error_message)
                return

            # 最初のフレームから動画のサイズを取得
            first_image_path = os.path.join(folder_path, images[0])
            frame = cv2.imread(first_image_path)
            
            if frame is None:
                with open("log.txt", "a") as f:
                    f.write("Failed to read the first image\n")
                messagebox.showerror("エラー", f"画像が読み込めませんでしたXDXDXD\n{first_image_path}を確認してください！！！")
                self.master.after(0, self.show_error_message)
                return

            height, width, layers = frame.shape

            # VideoWriterの設定
            with open("log.txt", "a") as f:
                f.write("VideoWriter started at " + str(datetime.datetime.now()) + "\n")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # 進行状況の更新
            self.progress["maximum"] = len(images)

            # 画像を動画に書き込み
            for i, image in enumerate(images):
                img_path = os.path.join(folder_path, image)
                frame = cv2.imread(img_path)
                
                if frame is None:
                    # ログに書き込む
                    with open("log.txt", "a") as f:
                        f.write(f"Failed to read image: {img_path}\n")
                    continue
                
                video.write(frame)
                
                # GUIスレッドで進行状況を更新
                self.master.after(0, self.update_progress, i + 1)

            video.release()
            with open("log.txt", "a") as f:
                f.write("VideoWriter stopped at " + str(datetime.datetime.now()) + "\n")

            # 成功メッセージ
            self.master.after(0, self.conversion_complete, "できましたよ!!!!!\noutput/" + output_name + "を確認してください！！！")

        except Exception as e:
            # エラーメッセージ
            self.master.after(0, self.show_error, str(e))

    def show_error_message(self):
        self.convert_button.config(state=tk.NORMAL)
        self.status_label.config(text="プロセスに失敗しましたXDXDXDXD")

    def update_progress(self, value):
        """進行状況バーを更新"""
        self.progress["value"] = value
        self.status_label.config(text=f"処理中: {value}/{self.progress['maximum']} フレーム")

    def conversion_complete(self, message):
        """変換完了時の処理"""
        self.convert_button.config(state=tk.NORMAL)
        self.status_label.config(text="変換完了!")
        messagebox.showinfo("成功", message)
        with open("log.txt", "a") as f:
            f.write("Conversion complete at " + str(datetime.datetime.now()) + "\n")

    def show_error(self, error_message):
        """エラー表示"""
        self.convert_button.config(state=tk.NORMAL)
        self.status_label.config(text="エラーが発生しました")
        messagebox.showerror("エラー", error_message)
        with open("log.txt", "a") as f:
            f.write("Conversion failed at " + str(datetime.datetime.now()) + "\n")

def main():
    print("Starting VisuaFlow application...")
    # ログファイルを作成
    with open("log.txt", "w") as f:
        f.write("Log started at " + str(datetime.datetime.now()) + "\n")
    root = tk.Tk()
    print("Tk root window created")
    app = ImageToVideoConverter(root)
    print("ImageToVideoConverter initialized")
    root.mainloop()
    print("Mainloop started")

if __name__ == '__main__':
    main()
