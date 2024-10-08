import requests
import random
from tkinter import *
from tkinter import ttk

# Trivia API에서 퀴즈 질문을 가져오는 함수
def fetch_questions(category, limit, difficulty):
    url = f"https://the-trivia-api.com/api/questions?categories={category}&limit={limit}&difficulty={difficulty}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # API로부터 데이터를 성공적으로 받아온 경우, JSON 형식의 데이터를 반환
    else:
        result_label.config(text=f"Failed to retrieve data: {response.status_code}", fg="red")  # 실패한 경우 오류 메시지 출력
        return []

# 다음 질문을 표시하는 함수
def next_question():
    global current_question, question_index
    if question_index < len(questions):
        current_question = questions[question_index]  # 현재 질문을 가져옴
        question_index += 1  # 질문 인덱스를 증가시킴
        question_label.config(text=current_question["question"])  # 질문 텍스트 업데이트
        options = current_question["incorrectAnswers"] + [current_question["correctAnswer"]]
        random.shuffle(options)  # 답변 옵션을 섞음

        for i, option in enumerate(options):
            buttons[i].config(text=option, command=lambda opt=option: check_answer(opt))  # 각 버튼에 답변 옵션과 클릭 이벤트를 설정
    else:
        show_score()  # 모든 질문이 끝났으면 점수를 보여줌

# 사용자가 답변을 선택했을 때 호출되는 함수
def check_answer(selected_option):
    global correct_answers
    correct_answer = current_question["correctAnswer"]
    if selected_option == correct_answer:
        result_label.config(text="Correct!", fg="green")  # 정답인 경우 'Correct!'를 초록색으로 표시
        correct_answers += 1  # 정답 수를 증가시킴
    else:
        result_label.config(text=f"Wrong! The correct answer was: {correct_answer}", fg="red")  # 오답인 경우 'Wrong!'을 빨간색으로 표시하고 정답을 보여줌
    next_question()  # 다음 질문으로 넘어감

# 퀴즈 완료 후 점수를 계산하고 보여주는 함수
def show_score():
    score = int((correct_answers / len(questions)) * 100)  # 정답률을 백분율로 계산
    result_label.config(text=f"You have completed the quiz! Your score is {correct_answers}/{len(questions)} ({score}%)", fg="green")
    start_button.config(state=NORMAL)  # 퀴즈 완료 후 다시 시작 버튼을 활성화

# 퀴즈 시작을 위한 설정 함수
def start_quiz():
    global questions, question_index, correct_answers
    limit = int(num_questions.get())  # 사용자가 선택한 질문 개수를 가져옴
    category = selected_category.get()  # 사용자가 선택한 카테고리를 가져옴
    difficulty = selected_difficulty.get()  # 사용자가 선택한 난이도를 가져옴

    questions = fetch_questions(category, limit, difficulty)  # API에서 질문 데이터를 가져옴
    if questions:
        question_index = 0  # 첫 번째 질문부터 시작
        correct_answers = 0  # 정답 수 초기화
        result_label.config(text="")  # 결과 레이블 초기화
        next_question()  # 첫 번째 질문을 표시
        start_button.config(state=DISABLED)  # 퀴즈 진행 중에는 시작 버튼을 비활성화

# 카테고리 선택 시 호출되는 함수
def select_category(cat):
    selected_category.set(cat)  # 선택된 카테고리 값을 저장
    category_label.config(text=f"Selected Category: {cat.capitalize()}")  # 선택된 카테고리를 라벨에 표시
    
# 난이도 선택 시 호출되는 함수
def select_difficulty(diff):
    selected_difficulty.set(diff)  # 선택된 난이도 값을 저장
    difficulty_label.config(text=f"Selected Difficulty: {diff.capitalize()}")  # 선택된 난이도를 라벨에 표시

# GUI 설정
window = Tk()
window.title("Quiz Game")
window.geometry("700x800")  # 창 크기 설정

# 카테고리 선택 섹션
category_frame = Frame(window)
category_frame.pack(pady=10)

# 카테고리 라벨을 설정하고 가운데 정렬
category_label = Label(category_frame, text="Category:", font=('Arial', 12, 'bold'))
category_label.grid(row=0, column=0, padx=10, columnspan=2)

categories = ["science", "history", "sports", "music", "geography"]
selected_category = StringVar(value=categories[0])  # 기본 카테고리 값 설정

# 카테고리 버튼 생성 및 그리드에 배치
for i, cat in enumerate(categories):
    btn = Button(category_frame, text=cat.capitalize(), width=10, command=lambda c=cat: select_category(c))
    btn.grid(row=1, column=i, padx=5, pady=5)

# 사용자가 직접 카테고리를 입력할 수 있는 필드
category_entry = Entry(category_frame)
category_entry.grid(row=1, column=len(categories), padx=10)
category_entry.insert(0, "Or enter a category")  # 기본 텍스트 설정

# 문제 개수 선택 섹션
num_questions_label = Label(window, text="Number of Questions:", font=('Arial', 12, 'bold'))
num_questions_label.pack(pady=5)

num_questions = ttk.Combobox(window, values=[5, 10, 15, 20], state="readonly")
num_questions.set(5)  # 기본값 설정
num_questions.pack(pady=5)

# 난이도 선택 섹션
difficulty_frame = Frame(window)
difficulty_frame.pack(pady=10)

# 난이도 라벨을 설정하고 가운데 정렬
difficulty_label = Label(difficulty_frame, text="Difficulty:", font=('Arial', 12, 'bold'))
difficulty_label.grid(row=0, column=0, padx=10, columnspan=2)

difficulties = ["easy", "medium", "hard"]
selected_difficulty = StringVar(value=difficulties[0])  # 기본 난이도 값 설정

# 난이도 버튼 생성 및 그리드에 배치
for i, diff in enumerate(difficulties):
    btn = Button(difficulty_frame, text=diff.capitalize(), width=10, command=lambda d=diff: select_difficulty(d))
    btn.grid(row=1, column=i, padx=5, pady=5)

# 퀴즈 시작 버튼
start_button = Button(window, text="Start Quiz", command=start_quiz)
start_button.pack(pady=10)

# 퀴즈 질문과 답변을 표시할 프레임
quiz_frame = Frame(window)
quiz_frame.pack(pady=20)

# 질문을 표시하는 레이블
question_label = Label(quiz_frame, text="", font=("Arial", 14), wraplength=500)
question_label.pack(pady=10)

# 답변 옵션을 표시하는 버튼들
buttons = []
for i in range(4):  # 4개의 답변 옵션
    btn = Button(quiz_frame, text="", font=("Arial", 12), width=40)
    btn.pack(pady=5)
    buttons.append(btn)

# 결과를 표시하는 레이블
result_label = Label(window, text="", font=("Arial", 14))
result_label.pack(pady=10)

# 전역 변수 초기화
questions = []
question_index = 0
correct_answers = 0
current_question = {}

# GUI 루프 시작
window.mainloop()