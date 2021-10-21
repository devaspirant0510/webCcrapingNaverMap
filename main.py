from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd

# options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument(
#     "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

# 판다스 데이터저장할 리스트
data_frame_list = []
# 저장할 파일 이름
file_name = "filename"

# 크롬 드라이버
driver = webdriver.Chrome()

# 스타벅스 검색결과 URL
driver.get("https://map.naver.com/v5/search/%EC%8A%A4%ED%83%80%EB%B2%85%EC%8A%A4")

# html 소스 읽기전에 페이지 로딩시간 네트워크 상태에따라 조절하시면 됩니다.
time.sleep(2)  # 2초동안 대기 페이지 로딩 대기
main_soup = BeautifulSoup(driver.page_source, "lxml")  # lxml 이라는 라이브러리를 설치하면 html.parser 보다 빨리 읽는다고 합니다.

page_number = 2  # 몇페이지 조회할건지 네이버지도는 한페이지에 50개씩 나옴
for page in range(page_number):
    for idx in range(1, 51):
        # 네이버지도에서 스타벅스 검색하면 주소정보는 안나와서 하나하나 클릭하는 로직
        # iframe 처리때문에 찾으려는 태그 부모중에 iframe 을 가지고 있으면 그 iframe 으로 switch 해줘야함
        driver.switch_to_frame("searchIframe")
        # 다음페이지로 넘겨서 조회
        if page != 0:
            # 다음페이지 버튼 클릭하고 페이지 로딩될때까지 대기
            next_page = driver.find_element_by_css_selector(
                f'#app-root > div > div > div._2ky45 > a:nth-child({page + 2})')
            next_page.click()
            time.sleep(2)
        # 스타벅스에대한 세부정보를 보기위해 아이템 클릭해 html 로 변환시켜 파싱
        main_view = driver.find_element_by_xpath(
            f'//*[@id="_pcmap_list_scroll_container"]/ul/li[{idx}]/div[1]/a/div[1]/div/span[1]')
        main_view.click()
        # 로딩
        time.sleep(2.5)
        # iframe 이동
        driver.switch_to_default_content()
        driver.switch_to_frame("entryIframe")

        # 현재 html 소스 가져옴
        get_cafe_html = driver.page_source
        # bs4 로 읽어옴
        convertBs4 = BeautifulSoup(get_cafe_html, "lxml")
        name = convertBs4.find("span", {"class": "_3XamX"}) # span 태그의 클래스가 _3XamX
        address = convertBs4.find("span", {"class": "_2yqUQ"})
        phone_number = convertBs4.find("span", {"class": "_3ZA0S"})

        # row 값 추가
        row = [name, address, phone_number]
        # 비어있는값 처리
        for colIdx, col in enumerate(row):
            if not col:
                row[colIdx] = None
            else:
                row[colIdx] = col.text
        # csv 로 만들 데이터 리스트에 추가
        data_frame_list.append(row)

        print(f"#{page * 50 + idx}:", ''.join(map(lambda x: "null" if x is None else x, row)))
        driver.switch_to_default_content()

# csv column 이름
header = ['매장이름', '주소', '전화번호']

# 아까 추가한 리스트를 데이터프레임으로 만듭니다.
df = pd.DataFrame(data_frame_list, columns=header)

# 데이터 프레임을 csv 로 만듭니다. mode='w' 는 덮어씌우기이고 mode='a' 는 이어서 작성하기 입니다. 한글은 깨지기 때문에 인코딩 속성을 넣어야 합니다.
df.to_csv(f"{file_name}.csv", mode='w', encoding='utf-8-sig')
