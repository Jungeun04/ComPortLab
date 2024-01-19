#Serial Class 정리

import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import queue
import json
import time


class SerialApp:
    def __init__(self, parent):
        self.parent = parent
        
        # Serial Port 변수 선언
        self.serial_port = None
        self.connected = False
        self.port_list = []
        self.init_ui(self.parent)
        self.search_ports()

        # 설정 파일 불러오기
        self.load_settings()

        # 스레드간 통신을 위한 queue
        self.data_queue = queue.Queue()

        # 종료 이벤트에 on_close 메서드를 바인딩

        self.update_ui()

    def init_ui(self,parent):

        self.serial_ui_frame = tk.Frame(parent)
        self.serial_ui_frame.grid(row=0, column=0, sticky='nsew')
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # 포트 선택 드롭다운 메뉴
        self.port_label = ttk.Label(self.serial_ui_frame, text="Select Port:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5)

        self.port_combobox = ttk.Combobox(self.serial_ui_frame)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.port_combobox['values'] = self.port_list

        # 연결 버튼
        self.connect_button = ttk.Button(self.serial_ui_frame, text="Connect", command=self.connect_port)
        self.connect_button.grid(row=0, column=2, padx=5, pady=5)

        # 해제 버튼
        self.disconnect_button = ttk.Button(self.serial_ui_frame, text="Disconnect", state=tk.DISABLED, command=self.disconnect_port)
        self.disconnect_button.grid(row=0, column=3, padx=5, pady=5)

        # 바우드 레이트 설정 드롭다운 메뉴
        self.baud_rate_label = tk.Label(self.serial_ui_frame, text="Baud Rate:")
        self.baud_rate_label.grid(row=1, column=0, padx=5, pady=5)

        self.baud_rate_combobox = ttk.Combobox(self.serial_ui_frame)
        self.baud_rate_combobox['values'] = list(reversed([300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]))
        self.baud_rate_combobox.current(0)  # 115200을 기본값으로 설정
        self.baud_rate_combobox.grid(row=1, column=1, padx=5, pady=5)

        # 데이터 전송 필드
        self.data_entry = ttk.Entry(self.serial_ui_frame)
        self.data_entry.grid(row=2, column=0, columnspan=3, padx=5, pady=5,sticky='ew')

        # 데이터 전송 버튼
        self.send_button = ttk.Button(self.serial_ui_frame, text="Send", command=lambda: self.send_data(self.data_entry.get()))
        self.send_button.grid(row=2, column=3, padx=5, pady=5)


        # 로그 표시를 위한 프레임 생성
        self.log_frame = ttk.Frame(self.serial_ui_frame)
        self.log_frame.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

        # 로그 표시 영역 (Text 위젯)
        self.log_text = tk.Text(self.log_frame, height=10, width=50)
        self.log_text.grid(row=0, column=0, sticky='nsew')

        # 스크롤 바 추가
        self.scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.log_text.config(yscrollcommand=self.scrollbar.set)

        # 프레임의 행과 열 설정
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)  # Text 위젯을 위한 공간
        self.log_frame.grid_columnconfigure(1, weight=0)  # Scrollbar를 위한 공간

        # 상태 업데이트 라벨
        self.status_label = tk.Label(self.serial_ui_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=99, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=5)


        # 행과 열의 비율 설정
        self.serial_ui_frame.grid_rowconfigure(0, weight=1)  # 첫 번째 행 설정
        self.serial_ui_frame.grid_rowconfigure(1, weight=1)  # 두 번째 행 설정
        self.serial_ui_frame.grid_rowconfigure(2, weight=1)  # 세 번째 행 설정
        self.serial_ui_frame.grid_rowconfigure(3, weight=1)  # 네 번째 행 설정
        self.serial_ui_frame.grid_rowconfigure(4, weight=1)  # 다섯 번째 행 설정

        self.serial_ui_frame.grid_columnconfigure(0, weight=1)  # 첫 번째 열 설정
        self.serial_ui_frame.grid_columnconfigure(1, weight=1)  # 두 번째 열 설정
        self.serial_ui_frame.grid_columnconfigure(2, weight=1)  # 세 번째 열 설정
        self.serial_ui_frame.grid_columnconfigure(3, weight=1)  # 네 번째 열 설정

    def update_ui(self):
        while not self.data_queue.empty():

            data = self.data_queue.get()

            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, data +'\n')
            self.log_text.see(tk.END)  # 스크롤을 최신 데이터 위치로 이동
            self.log_text.config(state=tk.DISABLED)
        self.parent.after(10, self.update_ui)  # 100ms 후에 다시 실행

    def search_ports(self): 
        # 사용 가능한 시리얼 포트를 검색하고 목록을 업데이트합니다.
        
        # 사용 가능한 포트 목록을 가져옵니다.
        ports = serial.tools.list_ports.comports()
        self.port_list = [port.device for port in ports]

        # 드롭다운 메뉴에 포트 목록을 업데이트합니다.
        self.port_combobox['values'] = self.port_list

        # 첫 번째 포트를 기본값으로 설정합니다(포트가 있는 경우).
        if self.port_list:
            self.port_combobox.current(0)

    def update_status(self, message):
        self.status_label.config(text=message)

    def connect_port(self):
        # 선택된 포트에 연결합니다.
        
        selected_port = self.port_combobox.get()
        selected_baud_rate = self.baud_rate_combobox.get()

        if not selected_port:
            self.update_status("No port selected.")
            return

        try:
            # 선택된 포트와 바우드 레이트를 사용하여 시리얼 연결을 설정합니다.
            self.serial_port = serial.Serial(port=selected_port, baudrate=int(selected_baud_rate), timeout=1)
            self.connected = True
            self.start_receiving_data()
            self.update_status(f"Connected to {selected_port} at {selected_baud_rate} baud.")
            
            # 연결 버튼 비활성화 및 해제 버튼 활성화
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
        except Exception as e:
            # 연결 실패 시 예외 처리
            self.handle_exception(e)
            self.update_status(f"Failed to connect: {str(e)}")
            self.connected = False

    def disconnect_port(self):
        if self.serial_port and self.serial_port.is_open:
            # 스레드 종료를 위한 플래그 설정
            self.connected = False

            # 수신 스레드가 종료될 때까지 기다립니다.
            if self.receiving_thread.is_alive():
                self.receiving_thread.join()

            try:
                # 시리얼 포트 연결을 닫습니다.
                self.serial_port.close()
                self.update_status("Disconnected from the port.")

                # 연결 버튼과 해제 버튼의 상태를 업데이트합니다.
                self.connect_button.config(state=tk.NORMAL)
                self.disconnect_button.config(state=tk.DISABLED)
            except Exception as e:
                # 연결 해제 중에 발생한 오류를 처리합니다.
                self.update_status("Failed to disconnect: " + str(e))
        else:
            # 이미 연결이 해제된 상태입니다.
            self.update_status("No active connection to disconnect.")


    def send_data(self, event=None):
        # 데이터를 시리얼 포트로 전송합니다.
        data = self.data_entry.get()
        if self.serial_port and self.serial_port.is_open:
            try:
                # 데이터를 UTF-8 형식으로 인코딩하여 전송합니다.
                self.serial_port.write(data.encode('utf-8'))
                self.update_status(f"Data sent: {data}")
                self.data_entry.delete(0, tk.END)
            except Exception as e:
                # 데이터 전송 중에 발생한 오류를 처리합니다.
                self.update_status(f"Failed to send data: {str(e)}")
        else:
            # 시리얼 포트가 열려 있지 않은 경우
            self.update_status("No open connection to send data.")

    def start_receiving_data(self):
        self.receiving_thread = threading.Thread(target=self.receive_data)
        self.receiving_thread.daemon = True  # 프로그램 종료시 스레드도 함께 종료
        self.receiving_thread.start()

    def receive_data(self):
        # 시리얼 포트에서 데이터를 수신합니다.
        while self.connected:
            try:
                if self.serial_port and self.serial_port.in_waiting:

                    # 짧은 지연을 추가하여 버퍼에 데이터가 충분히 쌓일 시간을 제공합니다.
                    time.sleep(0.1)  # 0.1초 지연

                    # 이 시점에서 더 많은 데이터가 도착했을 것으로 예상됩니다.
                    self.data_length = self.serial_port.in_waiting
                    raw_data = self.serial_port.read(self.data_length)
                    try:
                        self.data = raw_data.decode('utf-8')
                    except UnicodeDecodeError:
                        # UTF-8 디코딩 실패 시 이진 데이터로 처리
                        self.data = f"Binary data received: {raw_data}\n"
                    self.data_queue.put(self.data)

            except Exception as e:
                self.handle_exception(e)
                break  # 필요에 따라 루프 종료     

    def handle_exception(self, error):
        # 오류 메시지를 상태 바에 표시
        self.update_status(f"Error occurred: {error}")

        # 필요한 경우 로그 파일에 오류 기록
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error occurred: {error}\n")

    def save_settings(self):
        # 사용자 설정을 파일에 저장합니다.

        settings = {
            'port': self.port_combobox.get(),
            'baud_rate': self.baud_rate_combobox.get()
        }

        try:
            with open('serial_settings.json', 'w') as file:
                json.dump(settings, file)
            self.update_status("Settings saved successfully.")
        except Exception as e:
            self.update_status(f"Error saving settings: {e}")

    def load_settings(self):
        # 사용자 설정을 파일에서 불러옵니다.
        try:
            with open('serial_settings.json', 'r') as file:
                settings = json.load(file)
                self.port_combobox.set(settings.get('port', ''))
                self.baud_rate_combobox.set(settings.get('baud_rate', ''))
            self.update_status("Settings loaded successfully.")
        except Exception as e:
            self.update_status(f"Error loading settings: {e}")

    def on_close(self):
        self.save_settings()
        self.parent.destroy()

def add_tab():
    # 새 탭을 위한 프레임 생성
    new_tab_frame = ttk.Frame(notebook)
    # 새 탭에 SerialApp 인스턴스를 추가
    SerialApp(new_tab_frame)
    # Notebook에 새 탭 추가
    notebook.add(new_tab_frame, text=f"Serial App {notebook.index('end')+1}")



class NewApp:
    # 새로운 앱 클래스 정의
    def __init__(self, frame):
        # NewApp의 UI 구성
        # ...
        pass