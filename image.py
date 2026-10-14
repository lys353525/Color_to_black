import io
import json
import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageGrab

CONFIG_FILE = "config.json"

class GeminiImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("서창고 출제용 흑백 이미지 변환기 ver1.0    개발-퐁퐁남")
        self.root.geometry("800x720")

        self.input_image = None
        self.output_image = None

        self.create_widgets()
        
        # Ctrl+v / Ctrl+V 이벤트 바인딩
        self.root.bind("<Control-v>", self.paste_image_from_clipboard)
        self.root.bind("<Control-V>", self.paste_image_from_clipboard)

    def create_widgets(self):
        """GUI 구성 요소 생성"""
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        info_label = tk.Label(top_frame, text="클립보드에서 [Ctrl + V]를 눌러 이미지를 붙여넣으세요.", font=("Arial", 11, "bold"))
        info_label.pack(side=tk.LEFT)

        # 이미지 표시 영역
        image_frame = tk.Frame(self.root)
        image_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # 원본 이미지 패널
        left_frame = tk.LabelFrame(image_frame, text="원본 (붙여넣은 이미지)")
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_input = tk.Label(left_frame, text="[Ctrl + V]로 이미지를 붙여넣으세요", bg="#e0e0e0")
        self.lbl_input.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 변환 이미지 패널
        right_frame = tk.LabelFrame(image_frame, text="변환 결과 (선명하고 굵은 흑백 출제용)")
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_output = tk.Label(right_frame, text="변환 버튼을 누르면 결과가 표시됩니다", bg="#e0e0e0")
        self.lbl_output.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 수치 옵션 조절 영역 (추가된 부분)
        param_frame = tk.LabelFrame(self.root, text="⚙️ 세부 옵션 조절 (값을 변경 후 Enter 키를 누르면 즉시 반영됩니다)")
        param_frame.pack(fill=tk.X, padx=10, pady=5)

        # 1. 임계 범위 (Block Size)
        tk.Label(param_frame, text="임계 범위(홀수):").pack(side=tk.LEFT, padx=(10, 2))
        self.ent_block_size = tk.Entry(param_frame, width=5, justify="center")
        self.ent_block_size.insert(0, "31")
        self.ent_block_size.pack(side=tk.LEFT, padx=(0, 15))
        self.ent_block_size.bind("<Return>", lambda e: self.convert_image(show_popup=False))

        # 2. 세로 굵기 (Kernel Height)
        tk.Label(param_frame, text="세로 굵기:").pack(side=tk.LEFT, padx=(10, 2))
        self.ent_k_h = tk.Entry(param_frame, width=5, justify="center")
        self.ent_k_h.insert(0, "2")
        self.ent_k_h.pack(side=tk.LEFT, padx=(0, 15))
        self.ent_k_h.bind("<Return>", lambda e: self.convert_image(show_popup=False))

        # 3. 가로 굵기 (Kernel Width)
        tk.Label(param_frame, text="가로 굵기:").pack(side=tk.LEFT, padx=(10, 2))
        self.ent_k_w = tk.Entry(param_frame, width=5, justify="center")
        self.ent_k_w.insert(0, "2")
        self.ent_k_w.pack(side=tk.LEFT, padx=(0, 15))
        self.ent_k_w.bind("<Return>", lambda e: self.convert_image(show_popup=False))

        # 하단 컨트롤 영역
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_convert = tk.Button(
            action_frame, 
            text="✨ 선명하고 굵은 흑백 출제 이미지로 변환", 
            font=("Arial", 11, "bold"), 
            bg="#4CAF50", 
            fg="white", 
            command=lambda: self.convert_image(show_popup=True),
            state=tk.DISABLED
        )
        self.btn_convert.pack(fill=tk.X, pady=5)

        # 결과 처리 버튼 프레임
        self.result_btn_frame = tk.Frame(action_frame)
        
        self.btn_copy = tk.Button(self.result_btn_frame, text="📋 클립보드로 복사", command=self.copy_to_clipboard, width=20)
        self.btn_copy.pack(side=tk.LEFT, padx=10, expand=True)

        self.btn_save = tk.Button(self.result_btn_frame, text="💾 파일로 저장", command=self.save_to_file, width=20)
        self.btn_save.pack(side=tk.RIGHT, padx=10, expand=True)

    def paste_image_from_clipboard(self, event=None):
        """클립보드에서 이미지 가져오기"""
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.input_image = img
                self.display_image(self.input_image, self.lbl_input)
                self.btn_convert.config(state=tk.NORMAL)
                self.output_image = None
                self.lbl_output.config(image="", text="변환 버튼을 누르면 결과가 표시됩니다")
                self.result_btn_frame.pack_forget()
            else:
                messagebox.showwarning("알림", "클립보드에 이미지 데이터가 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"이미지를 붙여넣는 중 오류 발생: {e}")

    def display_image(self, img, label_widget):
        """라벨 크기에 맞게 리사이즈하여 표시"""
        display_size = (360, 420)
        img_copy = img.copy()
        img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        label_widget.config(image=photo, text="")
        label_widget.image = photo

    def convert_image(self, show_popup=True):
        """입력 필드에서 수치를 읽어와 변환 수행"""
        if not self.input_image:
            return

        # 텍스트 박스 값 검증 및 읽기
        try:
            block_size = int(self.ent_block_size.get().strip())
            k_h = int(self.ent_k_h.get().strip())
            k_w = int(self.ent_k_w.get().strip())

            # OpenCV 규격 예외 처리 (block_size는 3 이상의 홀수여야 함)
            if block_size < 3:
                block_size = 3
            if block_size % 2 == 0:
                block_size += 1
                self.ent_block_size.delete(0, tk.END)
                self.ent_block_size.insert(0, str(block_size))

            if k_h < 1: k_h = 1
            if k_w < 1: k_w = 1

        except ValueError:
            messagebox.showerror("입력 오류", "옵션 값에는 숫자만 입력해주세요.")
            return

        self.btn_convert.config(state=tk.DISABLED, text="변환 중... 잠시만 기다려주세요 ⏳")
        self.root.update()

        try:
            # 1. PIL 이미지를 NumPy 배열로 변환
            img_np = np.array(self.input_image.convert("RGB"))
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

            # 2. 양방향 필터(Bilateral Filter) 적용
            smooth = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

            # 3. 적응형 이진화 (사용자가 입력한 block_size 적용)
            binary = cv2.adaptiveThreshold(
                smooth, 
                255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                block_size, 
                8
            )

            # 4. 형태학적 연산 (사용자가 입력한 k_h, k_w 적용)
            kernel = np.ones((k_h, k_w), np.uint8)
            bold_binary = cv2.erode(binary, kernel, iterations=1)

            # 5. 경계면 매끄럽게 보정 (Anti-Aliasing)
            smoothed_line = cv2.GaussianBlur(bold_binary, (3, 3), 0)

            # 6. 결과를 PIL 이미지로 변환 및 출력
            self.output_image = Image.fromarray(smoothed_line)

            if self.output_image:
                self.display_image(self.output_image, self.lbl_output)
                self.result_btn_frame.pack(fill=tk.X, pady=5)
                if show_popup:
                    messagebox.showinfo("성공", "출제용 이미지 변환이 완료되었습니다!")

        except Exception as e:
            messagebox.showerror("오류", f"이미지 변환 중 오류 발생:\n{e}")
        finally:
            self.btn_convert.config(state=tk.NORMAL, text="✨ 선명하고 굵은 흑백 출제 이미지로 변환")

    def copy_to_clipboard(self):
        """결과 이미지를 윈도우 클립보드로 복사"""
        if not self.output_image:
            return

        try:
            output = io.BytesIO()
            self.output_image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]

            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

            messagebox.showinfo("성공", "변환된 이미지가 클립보드에 복사되었습니다.")
        except ImportError:
            messagebox.showwarning("알림", "클립보드 복사를 위해 'pywin32' 라이브러리가 필요합니다.\n명령어: pip install pywin32")
        except Exception as e:
            messagebox.showerror("오류", f"클립보드 복사 중 오류 발생: {e}")

    def save_to_file(self):
        """결과 이미지를 파일로 저장"""
        if not self.output_image:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"), ("모든 파일", "*.*")],
            title="출제용 이미지 저장"
        )
        if file_path:
            try:
                self.output_image.save(file_path)
                messagebox.showinfo("성공", f"파일이 성공적으로 저장되었습니다:\n{file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"파일 저장 실패: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeminiImageApp(root)
    root.mainloop()