import sys
import requests
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QComboBox, QWidget, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, QTimer

class QuizGame(QMainWindow):
    def __init__(self):
        super().__init__()

        # 창의 크기 조정
        self.setWindowTitle("Quiz Game")
        self.setGeometry(100, 100, 1200, 800)  # 크기를 줄임

        self.questions = []
        self.current_question_index = 0
        self.correct_answers = 0

        # 메인 위젯과 레이아웃 설정
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 질문 표시 영역 (위쪽)

# 문제 표시 영역 (위쪽)
        self.question_label = QLabel("", self)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFrameShape(QFrame.Box)
        self.question_label.setStyleSheet("font-size: 24px; padding: 20px; background-color: #D6EAF8;")  # 배경색 추가
        self.question_label.setWordWrap(True)
        main_layout.addWidget(self.question_label)

        # 답변 버튼 영역
        self.answer_buttons_layout = QVBoxLayout()
        self.answer_buttons = []
        for i in range(4):
            btn = QPushButton(f"", self)
            # 답변 버튼 영역에서 background-color 설정을 다른 색으로 테스트
            btn.setStyleSheet("font-size: 20px; padding: 10px; background-color: #CCCCCC;")  # 회색 배경색
            # 배경색 추가
            btn.setVisible(False)
            self.answer_buttons.append(btn)
            btn.clicked.connect(lambda _, b=btn: self.check_answer(b))
            self.answer_buttons_layout.addWidget(btn)

        main_layout.addLayout(self.answer_buttons_layout)



        # 결과 표시 영역 (보기와 카테고리 버튼 사이에 위치)
        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        # 폰트 크기와 패딩을 조정하여 한 줄 크기로 설정
        self.result_label.setStyleSheet("font-size: 18px; color: green; padding: 5px;")
        self.result_label.setFixedHeight(30)  # 높이를 30px로 고정하여 한 줄 크기로 설정
        main_layout.addWidget(self.result_label)

        # 카테고리, 난이도 및 설정 영역 (아래쪽)
        settings_layout = QGridLayout()
        main_layout.addLayout(settings_layout)

        # 카테고리 선택 버튼
        self.category_buttons = []
        categories = ["All", "Science", "History", "Sports", "Music", "Geography"]  # "All" 옵션 추가
        self.category_label = QLabel("Selected Category: None", self)
        self.category_label.setAlignment(Qt.AlignCenter)
        self.category_label.setStyleSheet("font-size: 24px; padding: 10px;")
        settings_layout.addWidget(self.category_label, 0, 0, 1, len(categories))

        self.selected_category = ""

        for i, category in enumerate(categories):
            btn = QPushButton(category, self)
            btn.setCheckable(True)
            btn.setStyleSheet("font-size: 18px; padding: 5px;")
            btn.clicked.connect(lambda checked, cat=category: self.select_category(cat))
            self.category_buttons.append(btn)
            settings_layout.addWidget(btn, 1, i)

        # Or enter a category (입력)
        self.custom_category_input = QPushButton("Or enter a category", self)
        self.custom_category_input.setStyleSheet("font-size: 18px; padding: 5px;")
        settings_layout.addWidget(self.custom_category_input, 1, len(categories), 1, 1)

        # 문제 개수 설정
        num_questions_label = QLabel("Number of Questions:", self)
        num_questions_label.setAlignment(Qt.AlignCenter)
        num_questions_label.setStyleSheet("font-size: 24px; padding: 10px;")
        settings_layout.addWidget(num_questions_label, 2, 0)

        self.num_questions_combo = QComboBox(self)
        self.num_questions_combo.addItems(["5", "10", "15", "20"])
        self.num_questions_combo.setStyleSheet("font-size: 18px;")
        settings_layout.addWidget(self.num_questions_combo, 2, 1)

        # 난이도 선택 버튼
        self.difficulty_label = QLabel("Selected Difficulty:", self)
        self.difficulty_label.setAlignment(Qt.AlignRight)
        self.difficulty_label.setStyleSheet("font-size: 24px; padding-right: 10px;")
        settings_layout.addWidget(self.difficulty_label, 3, 0)

        self.selected_difficulty = ""

        difficulties = ["Easy", "Medium", "Hard"]
        self.difficulty_buttons = []
        for i, difficulty in enumerate(difficulties):
            btn = QPushButton(difficulty, self)
            btn.setCheckable(True)
            btn.setStyleSheet("font-size: 18px; padding: 5px;")
            btn.clicked.connect(lambda checked, diff=difficulty: self.select_difficulty(diff))
            self.difficulty_buttons.append(btn)
            settings_layout.addWidget(btn, 3, i + 1)

        # 퀴즈 시작 버튼
        self.start_button = QPushButton("Start Quiz", self)
        self.start_button.setStyleSheet("font-size: 24px; padding: 10px;")
        settings_layout.addWidget(self.start_button, 4, 0, 1, len(difficulties) + 1)
        self.start_button.clicked.connect(self.start_quiz)

        # QSizePolicy 설정
        # For the quiz and answer sections
        self.question_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for button in self.answer_buttons:
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # For the category and difficulty selection section s
        self.category_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.difficulty_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def select_category(self, category):
        if category == "All":
            self.selected_category = ""  # "All"을 선택하면 빈 문자열로 설정하여 모든 카테고리에서 문제를 가져옴
        else:
            self.selected_category = category.lower()
        self.category_label.setText(f"Selected Category: {category}")

    def select_difficulty(self, difficulty):
        self.selected_difficulty = difficulty.lower()
        self.difficulty_label.setText(f"Selected Difficulty: {difficulty}")

    def fetch_questions(self):
        url = f"https://the-trivia-api.com/api/questions?categories={self.selected_category}&limit={self.num_questions_combo.currentText()}&difficulty={self.selected_difficulty}"
        response = requests.get(url)
        if response.status_code == 200:
            self.questions = response.json()
        else:
            self.result_label.setText(f"Failed to retrieve questions: {response.status_code}")
            self.questions = []

    def start_quiz(self):
        self.current_question_index = 0
        self.correct_answers = 0
        self.result_label.setText("")

        # API에서 질문 가져오기
        self.fetch_questions()

        if self.questions:
            self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            current_question = self.questions[self.current_question_index]
            self.question_label.setText(current_question["question"])

            options = current_question["incorrectAnswers"] + [current_question["correctAnswer"]]
            random.shuffle(options)

            for i, btn in enumerate(self.answer_buttons):
                btn.setText(options[i])
                btn.setVisible(True)

        else:
            QTimer.singleShot(1000, self.show_final_score)  # 1초 후에 최종 점수를 표시

    def check_answer(self, btn):
        current_question = self.questions[self.current_question_index]
        if btn.text() == current_question["correctAnswer"]:
            self.result_label.setText("Correct!")
            self.correct_answers += 1
        else:
            self.result_label.setText(f"Wrong! The correct answer was: {current_question['correctAnswer']}")

        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            QTimer.singleShot(1000, self.display_question)  # 1초 후에 다음 질문을 표시
        else:
            QTimer.singleShot(1000, self.show_final_score)  # 마지막 문제 후 1초 후에 최종 점수를 표시

    def show_final_score(self):
        self.result_label.setText(f"Quiz finished! You got {self.correct_answers}/{len(self.questions)} correct.")


app = QApplication(sys.argv)
window = QuizGame()
window.show()
sys.exit(app.exec_())
