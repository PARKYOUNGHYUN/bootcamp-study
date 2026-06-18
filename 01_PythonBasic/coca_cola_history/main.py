'''
코카콜라 로고 앨범

- 작성자: 박영현
- 작성일자: 2026.01.07
'''
from tkinter import *
from tkinter.font import *
from PIL import Image, ImageTk

# 변수 선언 부분
DIRECTORY = 'images/'

MAIN_COLOR = '#F5EFE6'

CHANGE_YEARS = [1886, 1887, 1889, 1891, 1893, 1941, 1958, 1969, 1985, 2003, 2007] # 로고 변경 시작 연도
LOGO_COUNT = len(CHANGE_YEARS)

years_index = 0

# 함수 정의 부분
def click_next():
    global years_index
    years_index += 1
    
    if years_index == LOGO_COUNT - 1:
        btnNext.config(state=DISABLED) # 다음 로고가 존재하지 않는 경우, 다음 버튼 비활성화
        view_logo(str(CHANGE_YEARS[years_index]))
    else:
        view_logo(str(CHANGE_YEARS[years_index]), str(CHANGE_YEARS[years_index + 1]))
    if  years_index == 1:
        btnPrev.config(state=ACTIVE)

def click_main():
    '''메인화면'''
    view_logo('main')
    pLabel2.configure(text='🥤지금까지의 코카콜라 로고 역사🥤')

def click_prev():
    '''이전 버튼을 눌렀을 때'''
    global years_index
    years_index -= 1
    
    if years_index == 0:
        btnPrev.config(state=DISABLED) # 이전 로고가 존재하지 않는 경우, 이전 버튼 비활성화
    if years_index == LOGO_COUNT - 2:
        btnNext.config(state=ACTIVE)

    view_logo(str(CHANGE_YEARS[years_index]), str(CHANGE_YEARS[years_index + 1]))

def view_logo(*file_names):
    '''이미지와 연도 표시'''
    photo = read_image(file_names[0])
    pLabel1.configure(image=photo)
    pLabel1.image = photo

    text = file_names[0] + '년'
    if len(file_names) == 2:
        end_year = str(int(file_names[1])-1)
        if file_names[0] != end_year:
            text += ' ~ ' + end_year + '년'
    pLabel2.configure(text=text)

def read_image(file_name):
    '''이미지를 불러오는 함수'''
    try:
        photo = Image.open(DIRECTORY + file_name + '.png')
    except FileNotFoundError: # png 파일이 존재하지 않아서 에러가 발생할 경우, jpg파일로 불러옴
        photo = Image.open(DIRECTORY + file_name + '.jpg')

    photo = photo.resize((700, 300))
    photo = ImageTk.PhotoImage(photo)
    return photo

def pageUp(event):
    click_next()

def pageDown(event):
    click_prev()

# 메인 코드 부분
window = Tk()
window.geometry('750x400')
window.title('코카콜라 역사')
window.configure(background='#F5EFE6')

font = Font(family = 'Gulim', size = 18)
pLabel1 = Label(window, background='#FFFFFF', width=750, height=300)
pLabel2 = Label(window, fg=MAIN_COLOR, font=font, background='#000000')
click_main()
btnPrev = Button(window, text='← 이전', border=0, background=MAIN_COLOR, activebackground=MAIN_COLOR, command=click_prev)
btnMain = Button(window, text='메인', border=0, background=MAIN_COLOR, activebackground=MAIN_COLOR, command=click_main)
btnNext = Button(window, text='다음 →', border=0, background=MAIN_COLOR, activebackground=MAIN_COLOR, command=click_next)

pLabel1.pack(side=TOP, fill=X, ipadx=10, ipady=5, expand=1)
pLabel2.pack(side=TOP, fill=X, ipady=5)
btnPrev.pack(side=LEFT, fill=X, padx=(220, 0), ipady=10)
btnMain.pack(side=LEFT, fill=X, padx=100, ipady=10)
btnNext.pack(side=LEFT, fill=X, ipady=10)

window.mainloop()