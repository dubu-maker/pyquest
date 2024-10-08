import sys
import random
import string
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QListWidget, QInputDialog, QMenu, QListWidgetItem, QDialog
)
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt, QSize
from cryptography.fernet import Fernet

# 고정된 키를 로드하거나 생성
def load_key():
    try:
        with open('pass/secret.key', 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open('pass/secret.key', 'wb') as key_file:
            key_file.write(key)
        return key


# 암호화/복호화를 위한 Fernet 키 생성
key = load_key()
cipher_suite = Fernet(key)

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()  # UI 초기화

    def initUI(self):
        self.setWindowTitle('Password Manager')  # 창 제목 설정
        self.setGeometry(100, 100, 400, 300)  # 창 크기 설정

        # 레이아웃 설정
        layout = QVBoxLayout()

        # 패스워드 입력 또는 생성 안내 레이블
        self.label = QLabel('Enter your password or generate a new one:')
        layout.addWidget(self.label)

        # 패스워드 입력 필드 (비밀번호 모드)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 패스워드 생성 버튼
        self.generate_button = QPushButton('Generate Password')
        self.generate_button.clicked.connect(self.generate_password)
        button_layout.addWidget(self.generate_button)

        # 패스워드 복사 버튼
        self.copy_button = QPushButton('Copy Password')
        self.copy_button.clicked.connect(self.copy_password)
        button_layout.addWidget(self.copy_button)

        layout.addLayout(button_layout)

        # 패스워드 저장 버튼
        self.save_button = QPushButton('Save Password')
        self.save_button.clicked.connect(self.save_password)
        layout.addWidget(self.save_button)

        # 저장된 패스워드 목록 보기 버튼
        self.list_button = QPushButton('List Saved Passwords')
        self.list_button.clicked.connect(self.open_password_list_dialog)
        layout.addWidget(self.list_button)

        # 메인 윈도우에 레이아웃 설정
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # 랜덤한 패스워드를 생성하는 함수
    def generate_password(self):
        length = 12  # 패스워드 길이
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(length))
        self.password_input.setText(password)  # 생성된 패스워드를 입력 필드에 표시

    # 패스워드를 클립보드에 복사하는 함수
    def copy_password(self):
        clipboard = QApplication.clipboard()
        password = self.password_input.text()
        clipboard.setText(password)
        QMessageBox.information(self, 'Success', 'Password copied to clipboard!')

    # 패스워드를 저장하는 함수
    def save_password(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, 'Warning', 'No password to save!')
            return

        usage = self.get_usage()  # 사용 용도 입력받기
        if not usage:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간 기록

        encrypted_password = cipher_suite.encrypt(password.encode())  # 패스워드 암호화

        data = {
            'usage': usage,
            'password': encrypted_password.decode(),
            'timestamp': timestamp
        }

        try:
            with open('passwords.json', 'r') as f:
                passwords = json.load(f)  # 기존 패스워드 파일 로드
        except FileNotFoundError:
            passwords = []  # 파일이 없으면 빈 리스트 생성

        passwords.append(data)  # 새 패스워드 추가

        with open('passwords.json', 'w') as f:
            json.dump(passwords, f, indent=4)  # 패스워드 저장

        QMessageBox.information(self, 'Success', 'Password saved successfully!')

    # 사용 용도를 입력받는 함수
    def get_usage(self):
        usage, ok = QInputDialog.getText(self, 'Save Password', 'Enter the usage (e.g., website name):')
        if not ok or not usage:
            return None
        return usage

    # 저장된 패스워드 목록을 보여주는 다이얼로그 창을 여는 함수
    def open_password_list_dialog(self):
        try:
            with open('passwords.json', 'r') as f:
                passwords = json.load(f)  # 패스워드 파일 로드
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'No passwords found!')
            return

        # 새로운 다이얼로그 창 생성
        dialog = QDialog(self)
        dialog.setWindowTitle('Saved Passwords')
        dialog.setGeometry(100, 100, 800, 600)  # 창 크기 설정

        # 패스워드 리스트를 보여주는 QListWidget
        list_widget = QListWidget(dialog)
        list_widget.setWordWrap(True)  # 줄 바꿈 설정
        for entry in passwords:
            item_text = f"Usage: {entry['usage']} | Encrypted Password: {entry['password']} | Created: {entry['timestamp']}"
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(780, 50))  # 항목 크기 조정
            list_widget.addItem(item)
        
        # 항목 더블 클릭 시 복호화 및 복사
        list_widget.itemDoubleClicked.connect(lambda: self.decrypt_and_copy_password(list_widget))
        # 우클릭 시 컨텍스트 메뉴 표시
        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(lambda pos: self.open_context_menu(pos, list_widget))

        # 다이얼로그 레이아웃 설정
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(list_widget)
        dialog.setLayout(dialog_layout)
        dialog.exec_()

    # 선택된 항목의 패스워드를 복호화하여 클립보드에 복사하는 함수
    def decrypt_and_copy_password(self, list_widget):
        selected_item = list_widget.currentItem()
        selected_text = selected_item.text()
        parts = selected_text.split('|')
        encrypted_password = parts[1].split(':')[1].strip()
        
        try:
            decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
            self.copy_to_clipboard(decrypted_password)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to decrypt password: {e}')

    # 텍스트를 클립보드에 복사하는 함수
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, 'Success', 'Decrypted password copied to clipboard!')

    # 컨텍스트 메뉴를 여는 함수 (우클릭 메뉴)
    def open_context_menu(self, position, list_widget):
        menu = QMenu()
        delete_action = menu.addAction("Delete Password")
        action = menu.exec_(list_widget.mapToGlobal(position))
        
        if action == delete_action:
            self.delete_password(list_widget)

    # 선택된 패스워드를 삭제하는 함수
    def delete_password(self, list_widget):
        selected_item = list_widget.currentItem()
        if selected_item:
            selected_text = selected_item.text()
            parts = selected_text.split('|')
            usage = parts[0].split(':')[1].strip()

            try:
                with open('passwords.json', 'r') as f:
                    passwords = json.load(f)
                
                # 선택된 패스워드 제거
                passwords = [p for p in passwords if p['usage'] != usage]

                with open('passwords.json', 'w') as f:
                    json.dump(passwords, f, indent=4)
                
                list_widget.takeItem(list_widget.row(selected_item))
                QMessageBox.information(self, 'Success', 'Password deleted successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to delete password: {e}')

# 애플리케이션 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordManager()
    ex.show()
    sys.exit(app.exec_())
