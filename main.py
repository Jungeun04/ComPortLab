#!/usr/bin/env python
# 리눅스에서 실행시 대비 Shebang

import tkinter as tk
from tkinter import ttk
from serial_app import SerialApp

# 메인 윈도우 생성
def main():
    root = tk.Tk()
    root.title("ComPortLab")
    root.minsize(width=500, height=350)  # 예시 크기, 필요에 따라 조절

    # 모니터 해상도 감지
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 모니터의 중심 좌표
    x = (screen_width / 2) - (500 / 2)
    y = (screen_height / 2) - (350 / 2)

    root.geometry(f'+{int(x)}+{int(y)}')

    # Notebook 위젯 생성
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # SerialApp을 위한 프레임 생성 및 Notebook에 추가
    serial_frame = ttk.Frame(notebook)
    serial_app = SerialApp(serial_frame)
    notebook.add(serial_frame, text="Serial App")
    

    root.mainloop()

if __name__ == "__main__":
    main()