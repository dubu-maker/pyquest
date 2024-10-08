import wx
import os
import textwrap
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 인스턴스 생성
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

        self.SetTitle("Maze Game")
        self.SetSize(1024, 1024)  # 창 크기를 1024x1024로 설정
        
        self.panel = wx.Panel(self)

        # 오프닝 이미지 로드
        opening_image = wx.Image("maze_game_start.png", wx.BITMAP_TYPE_ANY).Scale(1024, 1024)
        self.bitmap = wx.StaticBitmap(self.panel, -1, wx.Bitmap(opening_image), (0, 0))

        # 패널에 키보드 및 마우스 클릭 이벤트 바인딩
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_start)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_start)
        self.panel.SetFocus()

    def on_start(self, event):
        """키 또는 마우스 클릭 시 캐릭터 선택 화면으로 전환"""
        self.bitmap.Hide()  # 오프닝 이미지 숨기기
        self.show_character_selection()

    def show_character_selection(self):
        """캐릭터 선택 화면을 표시"""
        # 패널에 수직 레이아웃 설정
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 상단에 텍스트를 표시할 영역 추가
        self.message_text = wx.StaticText(self.panel, label="Please select a job:")
        self.vbox.Add(self.message_text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        # 그리드 레이아웃 설정 (4x4)
        self.grid_sizer = wx.GridSizer(4, 4, 10, 10)

        # 직업 리스트
        jobs = ["Warrior", "Paladin", "Hunter", "Mage", "Warlock", "Rogue", "Assassin"]

        # 각 직업을 버튼으로 추가
        for job in jobs:
            button = wx.Button(self.panel, label=job)
            
            # 폰트 크기 조정
            font = button.GetFont()
            font.PointSize += 10  # 폰트 크기 증가
            button.SetFont(font)
            
            button.Bind(wx.EVT_BUTTON, self.on_job_select)
            self.grid_sizer.Add(button, 0, wx.EXPAND)

        # 남아있는 공간을 빈 공간으로 채우기
        for _ in range(16 - len(jobs)):
            self.grid_sizer.Add(wx.StaticText(self.panel), 0, wx.EXPAND)

        self.vbox.Add(self.grid_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # 선택된 직업을 표시할 레이블 추가 (처음에는 숨김)
        self.selected_job_text = wx.StaticText(self.panel, label="")
        font = self.selected_job_text.GetFont()
        font.PointSize += 20  # 폰트 크기 증가
        font = font.Bold()
        self.selected_job_text.SetFont(font)
        self.vbox.Add(self.selected_job_text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        # 설명 텍스트를 표시할 StaticText 위젯 추가
        self.description_text = wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT)
        font = self.description_text.GetFont()
        font.PointSize += 10  # 폰트 크기 증가
        self.description_text.SetFont(font)
        self.vbox.Add(self.description_text, 1, wx.EXPAND | wx.ALL, 10)

        self.panel.SetSizer(self.vbox)
        self.panel.Layout()  # 레이아웃 적용

        # 다음 단계로 이동 버튼 추가
        self.next_button = wx.Button(self.panel, label="Next")
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next_click)
        self.vbox.Add(self.next_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

    def on_job_select(self, event):
        """직업 선택 시 호출되는 함수"""
        button = event.GetEventObject()
        selected_job = button.GetLabel()
        self.selected_job_text.SetLabelText(f"You selected {selected_job}!")
        self.selected_job_text.Show()  # 레이블 표시
        
        # OpenAI API를 통해 시나리오 생성
        dm_response = self.get_dm_response(selected_job)
        wrapped_text = textwrap.fill(dm_response, width=70)
        self.description_text.SetLabelText(wrapped_text)
        self.description_text.Show()  # 설명 텍스트 표시
        self.panel.Layout()  # 레이아웃 새로고침

    def get_dm_response(self, selected_job):
        """OpenAI API를 사용하여 던전 마스터의 위기 상황 시나리오 생성"""
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Create a scenario where a {selected_job} faces an imminent and dangerous situation in a dungeon. The scenario should describe a moment of danger where the adventure is just about to begin, but not end. Write it in Korean."
                }
            ],
            model="gpt-3.5-turbo",
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

    def on_next_click(self, event):
        """다음 버튼 클릭 시 호출되는 함수"""
        self.message_text.Hide()
        for child in self.grid_sizer.GetChildren():
            child.GetWindow().Hide()  # 그리드의 각 버튼들을 숨김
        self.next_button.Hide()
        
        # 유저 액션 선택을 위한 텍스트 추가
        self.user_action_prompt = wx.StaticText(self.panel, label="어떻게 하시겠습니까? 선택하세요:")
        font = self.user_action_prompt.GetFont()
        font.PointSize += 15  # 폰트 크기 증가
        self.user_action_prompt.SetFont(font)
        self.vbox.Add(self.user_action_prompt, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        # 액션 버튼들을 4x4 그리드로 배치
        action_grid_sizer = wx.GridSizer(4, 4, 10, 10)
        actions = ["Attack", "Defend", "Run", "Hide"]

        for action in actions:
            action_button = wx.Button(self.panel, label=action, size=(200, 50))
            action_button.Bind(wx.EVT_BUTTON, self.on_action_select)
            action_grid_sizer.Add(action_button, 0, wx.EXPAND)

        # 그리드의 나머지 빈 공간을 채우기 위한 빈 텍스트 추가
        for _ in range(16 - len(actions)):
            action_grid_sizer.Add(wx.StaticText(self.panel, label=""), 0, wx.EXPAND)

        self.vbox.Add(action_grid_sizer, 1, wx.EXPAND | wx.ALL, 10)

        self.panel.SetSizer(self.vbox)
        self.panel.Layout()



    def on_action_select(self, event):
        """유저가 행동을 선택했을 때 호출되는 함수"""
        action = event.GetEventObject().GetLabel()
        # 여기서 선택된 행동에 따른 추가 로직을 구현할 수 있습니다.
        wx.MessageBox(f"You chose to {action}!", "Action Selected", wx.OK | wx.ICON_INFORMATION)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(None)
    frame.Show(True)
    app.MainLoop()
