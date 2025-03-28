# pyinstaller --noconsole --onefile --windowed  --add-data "images/icon.png;." test15.py

import sys
import json
import socket
import threading
import queue
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QDialog,QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QTabWidget, QLabel, QPushButton, QLineEdit, QGroupBox,
                            QFormLayout, QTableWidget, QHBoxLayout,
                            QTableWidgetItem, QMessageBox, QSpinBox, QCheckBox,
                            QFileDialog, QComboBox, QDoubleSpinBox, QScrollArea,
                            QGridLayout, QSystemTrayIcon, QMenu, QAction,QSizePolicy,QHeaderView)
from PyQt5.QtCore import QTimer, QDate, pyqtSignal, QObject, Qt,QEvent
from PyQt5.QtGui import QIcon, QColor
import winreg
import os
import subprocess
import matplotlib.animation as animation
import time
from PyQt5.QtWidgets import QMessageBox

class SingleInstance:
    def __init__(self, port=12345):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.sock.bind(('localhost', self.port))
            # 새로운 인스턴스 실행 - 계속 진행
        except socket.error:
            # 이미 실행 중인 인스턴스가 있음
            msg = QMessageBox()
            msg.setWindowTitle('경고')
            msg.setText('프로그램이 이미 실행 중입니다.\n시스템 트레이에서 확인하세요.')
            msg.setFixedSize(400, 300)  # 창 크기 설정
            msg.exec_()
            sys.exit()
            
    def __del__(self):
        try:
            self.sock.close()
        except:
            pass



#초기 사용자 입력 만약에 입력이 되어 있으면 pass
class UserInfoDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.resize(450, 350)
        self.initUI()
        
    def initUI(self):
        self.setWindowIcon(QIcon("images/logo.png"))
        self.setWindowTitle('사용자 정보 입력')
        self.setModal(True)
        
        main_layout = QVBoxLayout()
        
        # 안내 메시지
        intro_label = QLabel('자세 모니터링을 시작하기 전에 사용자 정보를 입력해주세요.')
        intro_label.setAlignment(Qt.AlignCenter)
        intro_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(intro_label)
        
        # 입력 폼 그룹
        form_group = QGroupBox("사용자 정보")
        form_layout = QFormLayout()

        # 체중 입력
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0.0, 200.0)
        self.weight_input.setValue(self.settings.user_weight or 0.0)
        # self.weight_input.setSuffix(' kg')
        self.weight_input.setStyleSheet("padding: 5px;")
        self.weight_input.installEventFilter(self)  # 이벤트 필터 설치
        form_layout.addRow('체중:', self.weight_input)
        
        # 키 입력
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(0.0, 250.0)
        self.height_input.setValue(self.settings.user_height or 0.0)
        # self.height_input.setSuffix(' cm')
        self.height_input.setStyleSheet("padding: 5px;")
        self.height_input.installEventFilter(self)  # 이벤트 필터 설치
        form_layout.addRow('키:', self.height_input)
        
        # 성별 선택
        self.gender_input = QComboBox()
        self.gender_input.addItems(['선택하세요', 'Male', 'Female'])
        self.gender_input.setCurrentText(self.settings.user_gender or '선택하세요')
        self.gender_input.setStyleSheet("padding: 5px;")
        form_layout.addRow('성별:', self.gender_input)
        
        # 나이 입력
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 120)
        self.age_input.setValue(self.settings.user_age or 0)
        self.age_input.setStyleSheet("padding: 5px;")
        self.age_input.installEventFilter(self)  # 이벤트 필터 설치
        form_layout.addRow('나이:', self.age_input)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # 확인 버튼
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        confirm_button = QPushButton('확인')
        confirm_button.setStyleSheet("padding: 10px; font-size: 14px;")
        confirm_button.clicked.connect(self.validate_and_save)
        button_layout.addWidget(confirm_button)
        
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def eventFilter(self, obj, event):
        # 포커스가 주어질 때 값 초기화
        if event.type() == QEvent.FocusIn:
            if isinstance(obj, QDoubleSpinBox) or isinstance(obj, QSpinBox):
                if obj.value() == 0:
                    obj.clear()  # 포커스가 주어지면 값 초기화
        # 포커스를 잃을 때 값이 비어 있으면 0으로 설정
        elif event.type() == QEvent.FocusOut:
            if isinstance(obj, QDoubleSpinBox) and obj.value() == 0.0:
                obj.setValue(0.0)  # 포커스 잃으면 기본값 0으로 복원
            elif isinstance(obj, QSpinBox) and obj.value() == 0:
                obj.setValue(0)  # 포커스 잃으면 기본값 0으로 복원
        return super().eventFilter(obj, event)
        
    def validate_and_save(self):
        # 입력값 검증
        if self.weight_input.value() == 0:
            QMessageBox.warning(self, '입력 오류', '체중을 입력해주세요.')
            return
        
        if self.height_input.value() == 0:
            QMessageBox.warning(self, '입력 오류', '키를 입력해주세요.')
            return
        
        if self.gender_input.currentText() == '선택하세요':
            QMessageBox.warning(self, '입력 오류', '성별을 선택해주세요.')
            return
        
        if self.age_input.value() == 0:
            QMessageBox.warning(self, '입력 오류', '나이를 입력해주세요.')
            return
        
        # 설정 저장
        self.settings.user_weight = self.weight_input.value()
        self.settings.user_height = self.height_input.value()
        self.settings.user_gender = self.gender_input.currentText()
        self.settings.user_age = self.age_input.value()
        self.settings.save_settings()
        
        self.accept()



def check_initial_setup(settings):
    """사용자 정보가 설정되어 있는지 확인"""
    if (settings.user_weight == 0 or 
        settings.user_height == 0 or 
        not settings.user_gender or 
        settings.user_age == 0):
        return False
    return True


#창 크기 설정
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=2, height=1.5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        fig.tight_layout()

# 설정
class Settings:
    def __init__(self):
        # json 파일 만들기
        self.settings_file = 'app_settings.json'
        self.stats_file = 'posture_stats.json'
        self.load_settings()
        
        #데이터 값 가져오기
    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = self.get_default_settings()
        
        
        self.autostart = settings.get('autostart', False)
        self.background_execution = settings.get('background_execution', False)  # 추가
        self.toast_interval = settings.get('toast_interval', 1)
        self.toast_app = settings.get('toast_app', '')
        self.bad_posture_app = settings.get('bad_posture_app', '')
        self.host = settings.get('host', '')
        self.port = settings.get('port', 5000)
        self.saved_servers = settings.get('saved_servers', [])
        self.user_weight = settings.get('user_weight', 0.0)
        self.user_height = settings.get('user_height', 0.0)
        self.user_gender = settings.get('user_gender', '')
        self.user_age = settings.get('user_age', 0)
        self.bad_posture_alert_active = settings.get('bad_posture_alert_active', True)

    def save_settings(self):
        settings = {
            'autostart': self.autostart,
            'background_execution': self.background_execution,  # 추가
            'toast_interval': self.toast_interval,
            'toast_app': self.toast_app,
            'bad_posture_app': self.bad_posture_app,
            'bad_posture_alert_active': self.bad_posture_alert_active,
            'host': self.host,
            'port': self.port,
            'saved_servers': self.saved_servers,
            'user_weight': self.user_weight,
            'user_height': self.user_height,
            'user_gender': self.user_gender,
            'user_age': self.user_age
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)


    def load_stats(self):
        """저장된 자세 기록 데이터 로드"""
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_stats(self, stats):
        """자세 기록 데이터 저장"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

    def get_default_settings(self):
        return {
            'autostart': False,
            'background_execution': False,  # 추가
            'toast_interval': 1,
            'toast_app': '',
            'host': '',
            'port': 5000,
            'saved_servers': [],
            'user_weight': 0.0,
            'user_height': 0.0,
            'user_gender': '',
            'user_age': 0
        }
    
    def add_saved_server(self, host, port):
        server = f"{host}:{port}"
        if server not in self.saved_servers:
            self.saved_servers.append(server)
            self.save_settings()
    
    def remove_saved_server(self, server):
        if server in self.saved_servers:
            self.saved_servers.remove(server)
            self.save_settings()

    def clear_saved_servers(self):
        self.saved_servers = []
        self.save_settings()
        

class DataReceiver(QObject):
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.socket = None
        self.running = False

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def send_settings(self, settings_file):
        """서버로 설정 파일 전송"""
        if not self.socket:
            return False
        
        try:
            # 파일 읽기
            with open(settings_file, 'r') as f:
                settings_data = f.read()
            
            # 전송할 데이터 준비
            message = {
                'type': 'settings',
                'data': settings_data
            }
            
            # JSON으로 인코딩하고 newline 추가
            message_str = json.dumps(message) + '\n'
            
            # 데이터 전송
            self.socket.sendall(message_str.encode())
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"설정 파일 전송 오류: {str(e)}")
            return False

    def start_receiving(self):
        if self.socket:
            self.running = True
            thread = threading.Thread(target=self._receive_data)
            thread.daemon = True
            thread.start()

    def stop_receiving(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def _receive_data(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        values = json.loads(line)
                        self.data_received.emit(values)
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        self.error_occurred.emit(f"데이터 변환 오류: {str(e)}")
            except Exception as e:
                self.error_occurred.emit(f"데이터 수신 오류: {str(e)}")
                break

class PostureMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.data_receiver = DataReceiver()
        self.last_alert_time = 0 
        self.sensor_names = [
            "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
            "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16"
        ]
        self.pressure_data = {name: [] for name in self.sensor_names}
        self.times = []
        self.canvases = {}
        self.last_notification_time = datetime.now()
        self.notification_active = True
        self.max_data_points = 100
        self.current_start_index = 0
        self.stats_data = self.settings.load_stats() or []
        
        plt.rcParams['font.family'] = 'Malgun Gothic'

        self.initUI()
        self.load_saved_stats()
        self.showMaximized()
        
        self.data_receiver.data_received.connect(self.handle_new_data)
        self.data_receiver.error_occurred.connect(self.handle_error)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_graphs)
        self.update_timer.start(1000)

        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_notification)
        self.notification_timer.start(1000)


    def create_tray_icon(self):
        # 시스템 트레이 아이콘 생성
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.png'))  # 아이콘 파일 필요
        
        # 트레이 메뉴 생성
        tray_menu = QMenu()
        show_action = QAction("보이기", self)
        quit_action = QAction("종료", self)
        print("트레이 메뉴 생성됨")
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


    def load_saved_stats(self):
        """저장된 기록 불러오기"""
        stats = self.settings.load_stats()
        for stat in stats:
            row_position = self.stats_table.rowCount()
            self.stats_table.insertRow(row_position)
            
            self.stats_table.setItem(row_position, 0, QTableWidgetItem(stat['time']))
            self.stats_table.setItem(row_position, 1, QTableWidgetItem(stat['status']))
            self.stats_table.setItem(row_position, 2, QTableWidgetItem(stat['sensor_values']))
            self.stats_table.setItem(row_position, 3, QTableWidgetItem(str(stat['predicted_posture'])))  # int를 문자열로 변환
            
            # 상태에 따라 배경색 설정
            color = 'pink' if stat['status'] == '불량' else 'lightgreen'
            for col in range(4):  # 0부터 3까지 (모든 열 포함)
                self.stats_table.item(row_position, col).setBackground(QColor(color))

        
    def check_notification(self):
        if not self.notification_active or not self.settings.toast_app:
            return
            
        current_time = datetime.now()
        time_diff = (current_time - self.last_notification_time).total_seconds() / 60  # Convert to minutes
        
        if time_diff >= self.settings.toast_interval:
            self.show_notification()
            self.last_notification_time = current_time

    def show_notification(self):
        if self.settings.toast_app and os.path.exists(self.settings.toast_app):
            try:
                subprocess.Popen([self.settings.toast_app])
            except Exception as e:
                QMessageBox.warning(self, '알림 오류', f'알림 실행 실패: {str(e)}')

    def set_autostart(self, state):
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "PostureMonitor"
        
        try:
            if state:
                key_handle = winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key_handle, app_name, 0, winreg.REG_SZ, sys.argv[0])
            else:
                key_handle = winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(key_handle, app_name)
            winreg.CloseKey(key_handle)
        except Exception as e:
            QMessageBox.warning(self, '자동 시작 설정 오류', str(e))

    def reset_graph_data(self):
        """그래프 데이터 초기화"""
        self.times = []
        self.current_start_index = 0
        self.pressure_data = {name: [] for name in self.sensor_names}
        
        # 모든 그래프 캔버스 초기화
        for sensor_name, canvas in self.canvases.items():
            canvas.axes.clear()
            canvas.axes.grid(True)
            canvas.axes.set_title("")
            canvas.axes.set_xlabel("")
            canvas.axes.set_ylabel("")
            canvas.axes.set_ylim(0, 1024)
            canvas
            canvas.draw()

    def handle_new_data(self, data):
        if len(self.times) >= self.max_data_points // 2:
            self.times = self.times[self.max_data_points // 4:]
            for sensor_name in self.sensor_names:
                if self.pressure_data[sensor_name]:
                    self.pressure_data[sensor_name] = self.pressure_data[sensor_name][self.max_data_points // 4:]
            self.current_start_index += self.max_data_points // 4
        
        current_time = self.current_start_index + len(self.times)
        self.times.append(current_time)
        
        # 센서 데이터 처리
        sensor_values = data.get('sensor_data', {})
        
        # 각 센서 데이터 처리
        for sensor_name in self.sensor_names:
            value = sensor_values.get(sensor_name, 0)
            self.pressure_data[sensor_name].append(value)
        
        # 자세 상태 업데이트
        predicted_posture = data.get('predicted_posture', 0)
        self.update_posture_status(predicted_posture)
        self.log_posture_data(sensor_values, predicted_posture)


    
    def update_graphs(self):
        if not self.data_receiver.socket:
            return
            
        for sensor_name, canvas in self.canvases.items():
            if self.pressure_data[sensor_name] and len(self.pressure_data[sensor_name]) > 0:
                canvas.axes.clear()
                
                x_data = self.times[-100:]  # 최근 100개 데이터만 표시
                y_data = self.pressure_data[sensor_name][-100:]  # 최근 100개 데이터만 표시
                
                canvas.axes.plot(x_data, y_data, 'b-')
                canvas.axes.set_title(f'센서 {sensor_name}')
                
                canvas.axes.set_xlim(
                    self.current_start_index,
                    self.current_start_index + self.max_data_points // 2 + 10
                )
                canvas.axes.set_ylim(0, 1024)

                canvas.axes.grid(True)
                canvas.axes.set_xlabel('시간')
                canvas.axes.set_ylabel('압력')
                
                canvas.draw()

    def handle_error(self, error_message):
        QMessageBox.warning(self, '오류', error_message)

    def update_analysis_graphs(self):
        # 저장된 데이터 로드
        stats = self.settings.load_stats()
        
        if not stats:
            return
        
        # 시간별 자세 변화 그래프
        self.time_series_canvas.axes.clear()
        times = [stat['time'] for stat in stats]
        postures = [stat['predicted_posture'] for stat in stats]
        
        self.time_series_canvas.axes.plot(range(len(times)), postures, 'b-')
        self.time_series_canvas.axes.set_xticks(range(0, len(times), max(1, len(times)//10)))
        self.time_series_canvas.axes.set_xticklabels([times[i] for i in range(0, len(times), max(1, len(times)//10))], rotation=45)
        self.time_series_canvas.axes.set_ylabel('예측된 자세')
        self.time_series_canvas.axes.grid(True)
        self.time_series_canvas.draw()
        
        # 자세별 총 사용 시간 그래프
        self.duration_canvas.axes.clear()
        
        # 자세별 카운트 계산
        posture_counts = {}
        for stat in stats:
            posture = stat['predicted_posture']
            posture_counts[posture] = posture_counts.get(posture, 0) + 1
        
        postures = list(posture_counts.keys())
        counts = list(posture_counts.values())
        
        self.duration_canvas.axes.bar(postures, counts)
        self.duration_canvas.axes.set_xlabel('자세')
        self.duration_canvas.axes.set_ylabel('발생 횟수')
        self.duration_canvas.axes.grid(True)
        self.duration_canvas.draw()

    def update_posture_status(self, predicted_posture):
        current_time = time.time()
        COOLDOWN_SECONDS = 10
        
        if predicted_posture not in [0, 1]:
            status = '불량'
            color = 'red'
            
            if (current_time - self.last_alert_time) >= COOLDOWN_SECONDS:
                if self.settings.bad_posture_alert_active and self.settings.bad_posture_app:
                    try:
                        subprocess.Popen([self.settings.bad_posture_app])
                        self.last_alert_time = current_time
                    except Exception as e:
                        QMessageBox.warning(self, '알림 오류', f'나쁜 자세 알림 실행 실패: {str(e)}')
        else:
            status = '양호'
            color = 'green'
        
        self.posture_status_label.setText(f'현재 자세: {status} (예측 자세: {predicted_posture})')
        self.posture_status_label.setStyleSheet(f'color: {color}')

    def log_posture_data(self, sensor_values, predicted_posture):
        # 자세가 0일 때는 기록하지 않음
        if predicted_posture == 0:
            return
            
        current_time = datetime.now().strftime('%H:%M:%S')
        status = '불량' if predicted_posture != 1 else '양호'

        # 센서값들을 문자열로 변환
        sensor_values_str = ', '.join([f'{name}: {sensor_values.get(name, 0):.1f}' 
                                     for name in self.sensor_names])
        
        row_position = self.stats_table.rowCount()
        self.stats_table.insertRow(row_position)
        
        self.stats_table.setItem(row_position, 0, QTableWidgetItem(current_time))
        self.stats_table.setItem(row_position, 1, QTableWidgetItem(status))
        self.stats_table.setItem(row_position, 2, QTableWidgetItem(sensor_values_str))
        self.stats_table.setItem(row_position, 3, QTableWidgetItem(str(predicted_posture)))

        color = 'pink' if status == '불량' else 'lightgreen'
        for col in range(4):
            self.stats_table.item(row_position, col).setBackground(QColor(color))

        stat_entry = {
            'time': current_time,
            'status': status,
            'sensor_values': sensor_values_str,
            'predicted_posture': predicted_posture
        }
        self.stats_data.append(stat_entry)
        self.settings.save_stats(self.stats_data)



    def update_server_table(self):
        """서버 테이블 업데이트"""
        self.server_table.setRowCount(0)
        
        for i, server in enumerate(self.settings.saved_servers):
            row_position = self.server_table.rowCount()
            self.server_table.insertRow(row_position)
            
            # 서버 주소
            server_item = QTableWidgetItem(server)
            server_item.setTextAlignment(Qt.AlignCenter)  # 텍스트 가운데 정렬
            
            # 짝수/홀수 행에 따라 다른 배경색 설정
            if i % 2 == 0:
                server_item.setBackground(QColor("#E8F5E9"))  # 연한 민트색
            else:
                server_item.setBackground(QColor("#F1F8E9"))  # 연한 라임색
                
            self.server_table.setItem(row_position, 0, server_item)
            
            # 삭제 버튼을 위한 위젯
            delete_button = QPushButton('삭제')
            # delete_button.setFixedWidth(200) 
            # delete_button.setFixedHeight(30) 
            delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            delete_button.clicked.connect(lambda checked, s=server: self.remove_server(s))
            
            # 버튼이 있는 셀도 같은 배경색 설정
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.addWidget(delete_button)
            button_layout.setAlignment(Qt.AlignCenter)
            button_layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
            
            
            # if i % 2 == 0:
            #     button_widget.setStyleSheet("background-color: #E8F5E9;")
            # else:
            #     button_widget.setStyleSheet("background-color: #F1F8E9;")
                
            self.server_table.setCellWidget(row_position, 1, button_widget)

    def remove_server(self, server):
        """개별 서버 삭제"""
        reply = QMessageBox.question(self, '서버 삭제', 
                                f'서버 "{server}"를 삭제하시겠습니까?',
                                QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.settings.remove_saved_server(server)
            self.update_server_table()
            self.update_server_list()  # 콤보박스 업데이트
            self.statusBar().showMessage(f'서버 "{server}" 삭제됨')

    def clear_server_history(self):
        """모든 서버 기록 삭제"""
        if not self.settings.saved_servers:
            QMessageBox.information(self, '알림', '삭제할 서버 기록이 없습니다.')
            return

        reply = QMessageBox.question(self, '서버 기록 삭제', 
                                '모든 서버 기록을 삭제하시겠습니까?',
                                QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.settings.clear_saved_servers()
            self.update_server_table()
            self.update_server_list()  # 콤보박스 업데이트
            self.statusBar().showMessage('모든 서버 기록이 삭제되었습니다.')

            

    def browse_notification_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "알림 아이콘 선택",
            "",
            "실행 파일 (*.exe);;모든 파일 (*.*)"
        )
        if file_path:
            self.notification_app_path.setText(file_path)
            self.settings.toast_app = file_path
            self.settings.save_settings()

    def toggle_bad_posture_alert(self, state):
        self.settings.bad_posture_alert_active = bool(state)
        self.settings.save_settings()

    def browse_bad_posture_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "나쁜 자세 알림 프로그램 선택",
            "",
            "실행 파일 (*.exe);;모든 파일 (*.*)"
        )
        if file_path:
            self.bad_posture_app_path.setText(file_path)
            self.settings.bad_posture_app = file_path
            self.settings.save_settings()

    def initUI(self):
        self.setWindowTitle(' 로컬 디스크 C: 자세 교정 모니터링 시스템')
        self.setGeometry(100, 100, 1000, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.setWindowState(Qt.WindowMaximized)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # 설정 탭
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()

        # 테이블 높이 조절
        
        # 자동 시작 설정
        autostart_group = QGroupBox('시작 설정')
        autostart_layout = QVBoxLayout()
        
        self.autostart_checkbox = QCheckBox('윈도우 시작 시 자동 실행')
        self.autostart_checkbox.setChecked(self.settings.autostart)
        self.autostart_checkbox.stateChanged.connect(self.on_autostart_changed)
        
        self.background_execution_checkbox = QCheckBox('백그라운드 실행 활성화')
        self.background_execution_checkbox.setChecked(self.settings.background_execution)
        self.background_execution_checkbox.stateChanged.connect(self.on_background_execution_changed)
        
        autostart_layout.addWidget(self.autostart_checkbox)
        autostart_layout.addWidget(self.background_execution_checkbox)
        autostart_group.setLayout(autostart_layout)
        settings_layout.addWidget(autostart_group)
        # 서버 관리

        server_history_group = QGroupBox('서버 기록 관리')
        server_history_layout = QVBoxLayout()

        server_history_group.setLayout(server_history_layout)

        #높이 조절
        server_history_group.setFixedHeight(300)
        
        


        # 저장된 서버 목록을 보여주는 테이블
        self.server_table = QTableWidget()
        self.server_table.setColumnCount(2)
        self.server_table.setHorizontalHeaderLabels(['서버 주소', '동작'])
        self.server_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.server_table.verticalHeader().setVisible(False)
        self.server_table.setColumnWidth(1, 200)

        self.server_table.setAlternatingRowColors(True)
        server_history_layout.addWidget(self.server_table)

        self.update_server_table()


        clear_servers_button = QPushButton('모든 서버 기록 삭제')
        clear_servers_button.clicked.connect(self.clear_server_history)
        server_history_layout.addWidget(clear_servers_button)

        server_history_group.setLayout(server_history_layout)
        settings_layout.addWidget(server_history_group)
        

        # 알림 설정
        notification_group = QGroupBox('알림 설정')
        notification_layout = QFormLayout()
        
        self.notification_interval = QSpinBox()
        self.notification_interval.setRange(1, 60)
        self.notification_interval.setValue(self.settings.toast_interval)
        self.notification_interval.valueChanged.connect(self.on_interval_changed)
        notification_layout.addRow('알림 간격 (분):', self.notification_interval)

        self.notification_app_path = QLineEdit()
        self.notification_app_path.setText(self.settings.toast_app)
        browse_button = QPushButton('찾아보기')
        browse_button.clicked.connect(self.browse_notification_app)
        
        # 알림 활성화 체크박스 추가
        self.notification_active_checkbox = QCheckBox('알림 활성화')
        self.notification_active_checkbox.setChecked(True)
        self.notification_active_checkbox.stateChanged.connect(self.toggle_notification)
        notification_layout.addRow('알림 상태:', self.notification_active_checkbox)
    
        
        app_layout = QHBoxLayout()
        app_layout.addWidget(self.notification_app_path)
        app_layout.addWidget(browse_button)
        notification_layout.addRow('알림 프로그램:', app_layout)


        # 나쁜자세


        self.bad_posture_alert_checkbox = QCheckBox('나쁜 자세 알림 활성화')
        self.bad_posture_alert_checkbox.setChecked(self.settings.bad_posture_alert_active)
        self.bad_posture_alert_checkbox.stateChanged.connect(self.toggle_bad_posture_alert)
        notification_layout.addRow('나쁜 자세 알림 상태:', self.bad_posture_alert_checkbox)

        self.bad_posture_app_path = QLineEdit()
        self.bad_posture_app_path.setText(self.settings.bad_posture_app)
        bad_posture_browse_button = QPushButton('찾아보기')
        bad_posture_browse_button.clicked.connect(self.browse_bad_posture_app)
        
        bad_posture_app_layout = QHBoxLayout()
        bad_posture_app_layout.addWidget(self.bad_posture_app_path)
        bad_posture_app_layout.addWidget(bad_posture_browse_button)
        notification_layout.addRow('나쁜 자세 알림 프로그램:', bad_posture_app_layout)

        
        notification_group.setLayout(notification_layout)
        settings_layout.addWidget(notification_group)



        # 사용자 정보 설정
        user_info_group = QGroupBox('사용자 정보')
        user_info_layout = QFormLayout()

        self.user_weight = QDoubleSpinBox()
        self.user_weight.setRange(0.0, 300.0)
        self.user_weight.setValue(self.settings.user_weight)
        self.user_weight.valueChanged.connect(self.on_user_info_changed)
        user_info_layout.addRow('체중 (kg):', self.user_weight)

        self.user_height = QDoubleSpinBox()
        self.user_height.setRange(0.0, 200.0)
        self.user_height.setValue(self.settings.user_height)
        self.user_height.valueChanged.connect(self.on_user_info_changed)
        user_info_layout.addRow('키 (cm):', self.user_height)

        self.user_gender = QComboBox()
        self.user_gender.addItems(['', 'Male', 'Female'])
        self.user_gender.setCurrentText(self.settings.user_gender)
        self.user_gender.currentTextChanged.connect(self.on_user_info_changed)
        user_info_layout.addRow('성별:', self.user_gender)

        self.user_age = QSpinBox()
        self.user_age.setRange(0, 100)
        self.user_age.setValue(self.settings.user_age)
        self.user_age.valueChanged.connect(self.on_user_info_changed)
        user_info_layout.addRow('나이:', self.user_age)

        user_info_group.setLayout(user_info_layout)
        settings_layout.addWidget(user_info_group)
        
        settings_tab.setLayout(settings_layout)

        # 기존 탭들
        device_tab = self.create_device_tab()
        posture_tab = self.create_posture_tab()
        stats_tab = self.create_stats_tab()
        user_analysis_tab = self.create_user_analysis_tab() 

        # 탭 추가
        tabs.addTab(device_tab, '장치 정보')
        tabs.addTab(posture_tab, '측정')
        tabs.addTab(stats_tab, '기록 및 통계')
        tabs.addTab(user_analysis_tab, '사용자 분석')
        tabs.addTab(settings_tab, '설정')

    def on_background_execution_changed(self, state):
        """백그라운드 실행 설정 변경 처리"""
        self.settings.background_execution = bool(state)
        self.settings.save_settings()

    def toggle_notification(self, state):
        self.notification_active = bool(state)
        if state:
            self.last_notification_time = datetime.now()  # 활성화시 타이머 리셋

    def on_autostart_changed(self, state):
        self.settings.autostart = bool(state)
        self.set_autostart(bool(state))
        self.settings.save_settings()

    def on_interval_changed(self, value):
        self.settings.toast_interval = value
        self.settings.save_settings()
        self.last_notification_time = datetime.now()  # 간격 변경시 타이머 리셋

    def on_user_info_changed(self):
        self.settings.user_weight = self.user_weight.value()
        self.settings.user_height = self.user_height.value()
        self.settings.user_gender = self.user_gender.currentText()
        self.settings.user_age = self.user_age.value()
        self.settings.save_settings()

    def create_device_tab(self):
        device_tab = QWidget()
        device_layout = QVBoxLayout()
        
        status_group = QGroupBox('연결 상태')
        status_layout = QVBoxLayout()
        self.status_label = QLabel('연결 상태: 미연결')
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        device_layout.addWidget(status_group)

        settings_group = QGroupBox('연결 설정')
        settings_layout = QFormLayout()

        self.server_combo = QComboBox()
        self.server_combo.setEditable(True)
        self.update_server_list()
        self.server_combo.currentTextChanged.connect(self.on_server_selected)
        
        self.hostname_input = QLineEdit()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.settings.port)
        
        settings_layout.addRow('저장된 서버:', self.server_combo)
        settings_layout.addRow('서버 주소:', self.hostname_input)
        settings_layout.addRow('포트:', self.port_input)
        
        settings_group.setLayout(settings_layout)
        device_layout.addWidget(settings_group)

        buttons_layout = QHBoxLayout()
        connect_button = QPushButton('연결')
        connect_button.clicked.connect(self.connect_device)
        disconnect_button = QPushButton('연결 해제')
        disconnect_button.clicked.connect(self.disconnect_device)
        
        buttons_layout.addWidget(connect_button)
        buttons_layout.addWidget(disconnect_button)
        device_layout.addLayout(buttons_layout)
        
        device_tab.setLayout(device_layout)
        return device_tab

    def update_server_list(self):
        self.server_combo.clear()
        self.server_combo.addItem('')  # 빈 항목 추가
        for server in self.settings.saved_servers:
            self.server_combo.addItem(server)

    def on_server_selected(self, server_str):
        if server_str:
            try:
                host, port = server_str.split(':')
                self.hostname_input.setText(host)
                self.port_input.setValue(int(port))
            except:
                pass

    def create_posture_tab(self):
        posture_tab = QWidget()
        main_layout = QVBoxLayout()

        # 상태 그룹
        status_group = QGroupBox('현재 자세 상태')
        status_layout = QVBoxLayout()
        self.posture_status_label = QLabel('현재 자세: 측정 중...')
        status_layout.addWidget(self.posture_status_label)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # 스크롤 영역 생성
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        graph_widget = QWidget()
        graph_layout = QGridLayout()

        # 그래프 생성 (4x4 그리드로 변경)
        for i, sensor_name in enumerate(self.sensor_names):
            row = i // 4  # 4열로 변경
            col = i % 4
            
            group = QGroupBox(f'{sensor_name} 압력')
            group_layout = QVBoxLayout()
            
            canvas = MplCanvas(self, width=4, height=3, dpi=100)
            self.canvases[sensor_name] = canvas
            canvas.axes.grid(True)
            canvas.axes.set_ylim(0, 1024)
            canvas.draw()
            
            group_layout.addWidget(canvas)
            group.setLayout(group_layout)
            graph_layout.addWidget(group, row, col)

        graph_widget.setLayout(graph_layout)
        scroll.setWidget(graph_widget)
        main_layout.addWidget(scroll)
        
        posture_tab.setLayout(main_layout)
        return posture_tab

    def create_stats_tab(self):
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(['시간', '자세 상태', '압력값', '예측 자세'])
        
        # 각 열의 너비 설정
        self.stats_table.horizontalHeader().setStretchLastSection(False)  # 마지막 열 자동 늘리기 해제
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 시간
        self.stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)  # 자세 상태
        self.stats_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 압력값
        self.stats_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)  # 예측 자세
        
        # 열 너비 설정 (픽셀 단위)
        self.stats_table.setColumnWidth(0, 100)  # 시간
        self.stats_table.setColumnWidth(1, 100)  # 자세 상태
        self.stats_table.setColumnWidth(3, 100)  # 예측 자세
        
        self.stats_table.setAlternatingRowColors(True)
        stats_layout.addWidget(self.stats_table)
        
        stats_buttons_layout = QHBoxLayout()
        export_button = QPushButton('데이터 내보내기')
        export_button.clicked.connect(self.export_data)
        clear_button = QPushButton('기록 지우기')
        clear_button.clicked.connect(self.clear_stats)
        stats_buttons_layout.addWidget(export_button)
        stats_buttons_layout.addWidget(clear_button)
        stats_layout.addLayout(stats_buttons_layout)
        
        stats_tab.setLayout(stats_layout)
        return stats_tab

    def connect_device(self):
        host = self.hostname_input.text()
        port = self.port_input.value()

        if not host:
            QMessageBox.warning(self, '입력 오류', '서버 주소를 입력해주세요.')
            return

        self.statusBar().showMessage('연결 시도 중...')
        
        if self.data_receiver.connect(host, port):
            self.status_label.setText('연결 상태: 연결됨')
            self.status_label.setStyleSheet('color: green')
            
            try:
                # JSON 파일에서 weight와 height만 읽어서 전송
                with open('app_settings.json', 'r') as f:
                    settings = json.load(f)
                    user_data = {
                        "weight": settings.get("user_weight"),
                        "height": settings.get("user_height")
                    }
                
                # 사용자 데이터를 JSON 문자열로 변환하여 전송
                if self.data_receiver.socket.sendall(json.dumps(user_data).encode('utf-8')):
                    self.statusBar().showMessage('서버 연결 및 사용자 데이터 전송 성공')
                else:
                    self.statusBar().showMessage('서버 연결 성공, 사용자 데이터 전송 실패')
            
            except Exception as e:
                self.statusBar().showMessage(f'사용자 데이터 전송 실패: {str(e)}')
                print(f"Error sending user data: {e}")
            
            self.settings.host = host
            self.settings.port = port
            self.settings.add_saved_server(host, port)
            self.settings.save_settings()
            
            self.data_receiver.start_receiving()
        else:
            self.status_label.setText('연결 상태: 연결 실패')
            self.status_label.setStyleSheet('color: red')
            self.statusBar().showMessage('서버 연결 실패')

    def disconnect_device(self):
        self.data_receiver.stop_receiving()
        self.status_label.setText('연결 상태: 미연결')
        self.status_label.setStyleSheet('color: black')
        self.posture_status_label.setText('현재 자세: 분석 중...')  # 자세 상태 레이블 초기화
        self.posture_status_label.setStyleSheet('color: black')  # 자세 상태 색상 초기화
        self.statusBar().showMessage('서버 연결 해제됨')
        self.reset_graph_data()  # 그래프 데이터 초기화

    def export_data(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "데이터 내보내기",
                f'posture_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                "CSV 파일 (*.csv);;모든 파일 (*.*)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('시간,자세 상태,압력값,예측 자세\n')
                    for stat in self.stats_data:
                        f.write(f'{stat["time"]},{stat["status"]},{stat["sensor_values"]},{stat["predicted_posture"]}\n')
                QMessageBox.information(self, '내보내기 성공', f'데이터가 {filename}에 저장되었습니다.')
        except Exception as e:
            QMessageBox.warning(self, '내보내기 실패', f'데이터 내보내기 실패: {str(e)}')

    def clear_stats(self):
        reply = QMessageBox.question(self, '기록 삭제', 
                                   '모든 기록을 삭제하시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.stats_table.setRowCount(0)
            self.stats_data = []  # 데이터 리스트 초기화
            self.settings.save_stats(self.stats_data)  # 빈 데이터 저장
            self.statusBar().showMessage('기록이 삭제되었습니다.')


    def create_user_analysis_tab(self):
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout()
        
        # 시간별 자세 변화 그래프
        time_series_group = QGroupBox('시간별 자세 변화')
        time_series_layout = QVBoxLayout()
        
        time_canvas = MplCanvas(self, width=8, height=4, dpi=100)
        self.time_series_canvas = time_canvas
        time_series_layout.addWidget(time_canvas)
        time_series_group.setLayout(time_series_layout)
        analysis_layout.addWidget(time_series_group)
        
        # 자세별 총 사용 시간 그래프 
        duration_group = QGroupBox('자세별 총 사용 시간')
        duration_layout = QVBoxLayout()
        
        duration_canvas = MplCanvas(self, width=8, height=4, dpi=100)
        self.duration_canvas = duration_canvas
        duration_layout.addWidget(duration_canvas)
        duration_group.setLayout(duration_layout)
        analysis_layout.addWidget(duration_group)
        
        # 타이머 설정 (5초마다 업데이트)
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.update_analysis_graphs)
        self.analysis_timer.start(3000)  # 3000ms = 3초
        
        analysis_tab.setLayout(analysis_layout)
        return analysis_tab

    def quit_application(self):
        """트레이 아이콘에서 종료할 때 사용"""
        # 타이머 정리
        if hasattr(self, 'analysis_timer') and self.analysis_timer is not None:
            self.analysis_timer.stop()
        
        # 데이터 수신 중지
        self.data_receiver.stop_receiving()
        
        # 설정과 통계 저장
        self.settings.save_settings()
        self.settings.save_stats(self.stats_data)
        
        QApplication.quit()


    def closeEvent(self, event):
        # 백그라운드 실행 설정인 경우
        if self.settings.background_execution:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "자세 모니터링",
                "프로그램이 백그라운드에서 실행 중입니다.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            reply = QMessageBox.question(
                self, 
                '종료', 
                '프로그램을 종료하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 타이머 정리
                if hasattr(self, 'analysis_timer') and self.analysis_timer is not None:
                    self.analysis_timer.stop()
                
                # 데이터 수신 중지
                self.data_receiver.stop_receiving()
                
                # 설정과 통계 저장
                self.settings.save_settings()
                self.settings.save_stats(self.stats_data)
                
                event.accept()  # 이벤트 승인하여 종료 진행
                QApplication.quit()
            else:
                event.ignore()

def main():
    app = QApplication(sys.argv)
    
    # 프로그램이 이미 실행 중인지 확인
    socket_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_test.bind(("localhost", 12345))
    except socket.error:
        QMessageBox.warning(None, '실행 오류', '프로그램이 이미 실행 중입니다.')
        return
    finally:
        socket_test.close()

    app.setWindowIcon(QIcon("images/logo.png"))
    
    # 시스템 종료 시에도 정상 종료되도록 설정
    app.setQuitOnLastWindowClosed(False)
    
    ex = PostureMonitorApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()