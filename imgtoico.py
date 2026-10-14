import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def convert_to_ico():
    # 1. 원본 이미지 파일 선택
    file_path = filedialog.askopenfilename(
        title="이미지 파일 선택",
        filetypes=[
            ("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.webp"),
            ("모든 파일", "*.*")
        ]
    )
    
    if not file_path:
        return  # 파일 선택을 취소한 경우

    # 2. 저장할 ico 파일 경로 지정
    default_output = os.path.splitext(file_path)[0] + ".ico"
    save_path = filedialog.asksaveasfilename(
        title="ICO 파일 저장 위치 선택",
        initialfile=os.path.basename(default_output),
        defaultextension=".ico",
        filetypes=[("ICO 파일", "*.ico")]
    )
    
    if not save_path:
        return  # 저장을 취소한 경우

    # 3. ICO 변환 작업
    try:
        img = Image.open(file_path)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(save_path, format='ICO', sizes=icon_sizes)
        
        messagebox.showinfo("성공", f"ICO 파일이 성공적으로 생성되었습니다!\n\n저장 경로: {save_path}")
    except Exception as e:
        messagebox.showerror("오류", f"변환 과정에서 오류가 발생했습니다.\n{e}")

# GUI UI 구성
root = tk.Tk()
root.title("이미지 -> ICO 변환기")
root.geometry("380x150")
root.resizable(False, False)

label = tk.Label(root, text="JPG, PNG 이미지 파일을 ICO 아이콘으로 변환합니다.", pady=20)
label.pack()

btn_convert = tk.Button(root, text="이미지 파일 불러오기 & 변환", command=convert_to_ico, padx=10, pady=5)
btn_convert.pack()

root.mainloop()