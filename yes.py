# 트와이스 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    NoAlertPresentException,
    NoSuchWindowException,
    TimeoutException,
)
import time
import json
import traceback

# ChromeDriver 서비스 설정
driver_path = './chromedriver.exe'
service = Service(executable_path=driver_path)

# Chrome 실행
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 탐지 방지 옵션
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 최대 시도 횟수 및 모니터링 간격 설정
max_attempts = 10000
monitoring_interval = 0.5  # 초

# 1. Yes24 티켓 페이지로 이동 (쿠키 추가할 도메인으로 먼저 이동)
driver.get('https://ticket.yes24.com')

# 2. 저장된 쿠키 불러오기 (현재 도메인에 쿠키 추가)
try:
    with open('cookies.json', 'r') as cookies_file:
        cookies = json.load(cookies_file)
        for cookie in cookies:
            if 'sameSite' in cookie:
                del cookie['sameSite']
            driver.add_cookie(cookie)
    print("쿠키 로드 성공")
except Exception as e:
    print(f"쿠키 로드 실패: {e}")

# 3. 쿠키 추가 후 페이지 새로고침 (로그인 유지 확인)
driver.refresh()

# 4. 예매하기 버튼이 있는 페이지로 이동
driver.get('http://ticket.yes24.com/Special/51057')

# 5. 예매하기 버튼 클릭
try:
    book_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="mainForm"]/div[9]/div/div[4]/a[4]'))
    )
    book_button.click()  # 예매하기 버튼 클릭
    print("예매하기 버튼 클릭 완료")
except Exception as e:
    print(f"예매하기 버튼 클릭 오류: {e}")

# 팝업 처리 함수
def handle_alert():
    try:
        alert = driver.switch_to.alert  # 팝업창이 있을 경우 처리
        print(f"팝업 텍스트: {alert.text}")
        alert.accept()  # 팝업 닫기
    except NoAlertPresentException:
        pass  # 팝업이 없을 경우 아무 작업 안 함

# 팝업 처리 (필요할 때마다 호출)
handle_alert()

# 현재 열린 창의 핸들 저장
main_window = driver.current_window_handle

# 예매하기 버튼을 클릭한 후 새 창(또는 팝업창)이 열리는지 확인하고 제어를 전환
try:
    WebDriverWait(driver, 10).until(
        EC.number_of_windows_to_be(2)  # 새 창이 열릴 때 창의 수가 2개가 되길 기다림
    )
    all_windows = driver.window_handles
    for window in all_windows:
        if window != main_window:  # 새로운 창으로 제어를 넘김
            driver.switch_to.window(window)
            print("새 창으로 제어를 전환했습니다.")
            break
except Exception as e:
    print(f"새 창 제어 오류: {e}")

# 날짜 선택
try:
    date_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "2024-10-20"))  # 날짜 선택
    )
    date_button.click()
    print("날짜 선택 완료")
except Exception as e:
    print(f"날짜 선택 오류: {e}")

# 회차 선택 (1회차 선택)
try:
    time_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="ulTime"]/li[1]'))  # 회차 선택 (XPath 사용)
    )
    time_button.click()
    print("회차 선택 완료")
except Exception as e:
    print(f"회차 선택 오류: {e}")

# 좌석 선택
try:
    seat_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'btnSeatSelect'))  # 좌석 선택 버튼 (ID 사용)
    )
    seat_button.click()
    print("좌석 선택 완료")
except Exception as e:
    print(f"좌석 선택 오류: {e}")

def monitor_and_select_seat():
    attempts = 0
    failed_seat_ids = []  # 오류가 발생한 좌석의 id를 저장할 리스트

    while attempts < max_attempts:
        try:
            print(f"Attempt {attempts + 1} out of {max_attempts}")

            # 특정 횟수마다 진행 상황 메시지 출력
            if attempts % 100 == 0:
                print("스크립트가 정상적으로 실행 중입니다. Selenium이 잘 작동하고 있습니다.")

            # 기본 컨텐츠로 전환
            driver.switch_to.default_content()

            # 좌석 선택 프레임이 로드될 때까지 기다림
            try:
                iframe_seat = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.NAME, 'ifrmSeatFrame'))
                )
                driver.switch_to.frame(iframe_seat)
            except TimeoutException:
                time.sleep(monitoring_interval)
                attempts += 1
                continue  # 다음 시도로 넘어감

            # 선택 가능한 좌석만 찾기 (XPath 수정)
            seats = driver.find_elements(By.XPATH, "//div[starts-with(@id, 't') and @name='tk' and @title]")

            # 여기서 좌석의 개수를 출력합니다
            seat_count = len(seats)
            print(f"조건을 만족하는 좌석은 총 {seat_count}개입니다.")

            if seats:
                print(f"{seat_count}개의 선택 가능한 좌석을 찾았습니다.")
                print("좌석 목록:")
                for seat in seats:
                    seat_id = seat.get_attribute('id')
                    seat_title = seat.get_attribute('title')
                    print(f"- ID: {seat_id}, 정보: {seat_title}")
                    if seat_id in failed_seat_ids:
                        print(f"이미 선택 실패한 좌석 {seat_id}를 건너뜁니다.")
                        continue  # 이미 실패한 좌석은 건너뜁니다.

                    try:
                        seat.click()
                        print(f"좌석 {seat_id}를 선택했습니다.")

                        # 좌석 선택 확인 (알림 창 처리)
                        try:
                            WebDriverWait(driver, 1).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            alert.accept()
                            print(f"알림 창이 나타났습니다: {alert_text}")
                            # 알림 창이 나타났다면 좌석 선택에 실패한 것이므로 해당 좌석 id를 저장하고 다음 좌석으로 넘어갑니다.
                            failed_seat_ids.append(seat_id)
                            continue
                        except TimeoutException:
                            pass  # 알림 창이 없으면 좌석 선택 성공

                        # 좌석 클릭 후 바로 버튼 클릭 시도
                        try:
                            confirm_button = driver.find_element(By.XPATH, "//a[@href='javascript:ChoiceEnd();']")
                            confirm_button.click()
                            print("좌석선택완료 버튼을 클릭했습니다.")
                        except Exception as e:
                            print(f"버튼 클릭에 실패했습니다: {e}")
                            traceback.print_exc()
                            return False
                        return True  # 좌석 선택 및 확인 버튼 클릭 성공
                    except Exception as e:
                        print(f"좌석 {seat_id} 선택에 실패했습니다: {e}")
                        # 선택 실패한 좌석 id를 저장
                        failed_seat_ids.append(seat_id)
                        continue  # 다음 좌석으로 넘어감
                print("모든 좌석을 시도했지만 선택하지 못했습니다.")
            else:
                print("선택 가능한 좌석을 찾지 못했습니다.")
        except Exception as e:
            print(f"좌석 선택 시 문제가 발생했습니다: {e}")
            traceback.print_exc()

        # 대기 후 다시 시도
        time.sleep(monitoring_interval)
        attempts += 1

    return False  # 최대 시도 횟수 초과

# 좌석 선택 모니터링 시작
if monitor_and_select_seat():
    print("좌석 선택에 성공했습니다.")
    
    # 좌석 선택 후 Telegram으로 알림 전송
    token = '7616270521:AAGXLoX51E0H6iqbuBN9TfFq0WqoSphjK1c'

    chat_id = '7889718434'  # 확인된 Chat ID
    message = "좌석 선택이 완료되었습니다!"
    
    send_telegram_message(token, chat_id, message)

else:
    print("좌석 선택에 실패했습니다. 모니터링을 종료합니다.")

# '다음단계' 버튼 클릭 함수 정의
def click_next_step():
    try:
        # 기본 컨텐츠로 전환
        driver.switch_to.default_content()
        print("Attempting to click '다음단계' 버튼")

        # '다음단계' 버튼이 로드될 때까지 기다림
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@onclick='fdc_PromotionEnd();']/img[@alt='다음단계']"))
        )
        # 부모 <a> 태그 클릭
        parent_element = next_button.find_element(By.XPATH, "..")
        parent_element.click()
        print("'다음단계' 버튼을 클릭했습니다.")
    except Exception as e:
        print(f"'다음단계' 버튼 클릭에 실패했습니다: {e}")
        traceback.print_exc()
        return False
    return True

# Telegram 메시지 전송 함수
import requests

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(url, params=params)
    return response

# '다음단계' 버튼 클릭
if click_next_step():
    print("다음 단계로 이동했습니다.")
else:
    print("다음 단계로 이동하지 못했습니다.")

# 추가 작업이 필요하다면 여기에 작성합니다.