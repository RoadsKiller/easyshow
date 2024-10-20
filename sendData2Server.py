import requests
from bs4 import BeautifulSoup
import json
import time
import threading

# 全局变量
trustpilot_url = "https://www.trustpilot.com/review/example.com"
# 接口地址
api_url = "Your API"

def fetch_trustpilot_reviews():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }

    response = requests.get(trustpilot_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取评分数据
    grades_img_element = soup.find('div', {'class': 'star-rating_starRating__4rrcf'})
    grades_img = grades_img_element.find('img')['src'] if grades_img_element else "Image not found"

    meta_tag = soup.find('meta', {'property': 'og:title'})
    if meta_tag:
        content = meta_tag.get('content')
        parts = content.split('"')
        grades_name = parts[1] if len(parts) > 1 else "Name not found"
        score_part = parts[2].split("with ")[-1].split(" /")[0]
        rv_total_num = score_part.strip()
    else:
        grades_name = "Name not found"
        rv_total_num = "Rating not found"

    rv_total_num_element = soup.find('p', {'data-reviews-count-typography': 'true'})
    if rv_total_num_element:
        rv_total_num = rv_total_num_element.text.strip().split()[0]

    # 获取评论数据
    reviews = []
    review_elements = soup.find_all('div', {'class': 'styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ'})
    for index, review_element in enumerate(review_elements):
        url_element = review_element.find('a', {'class': 'link_internal__7XN06'})
        review_url = "https://www.trustpilot.com" + url_element['href'] if url_element else "URL not found"

        img_src = "Image not found"
        img_card = review_element.find('div', {'class': 'styles_reviewHeader__iU9Px'})
        if img_card:
            img_container = img_card.find('div', {'class': 'star-rating_starRating__4rrcf'})
            if img_container:
                img_element = img_container.find('img')
                img_src = img_element['src'] if img_element else "Image not found"

        time_container = review_element.find('div', {'class': 'styles_reviewHeader__iU9Px'})
        if time_container:
            time_element = time_container.find('time')
            review_time = time_element.text.strip() if time_element else "Time not found"

        title_element = review_element.find('h2', {'data-service-review-title-typography': 'true'})
        review_title = title_element.text.strip() if title_element else "Title not found"

        content_element = review_element.find('p', {'data-service-review-text-typography': 'true'})
        review_content = content_element.text.strip() if content_element else "Content not found"

        username_container = review_element.find('a', {'name': 'consumer-profile'})
        if username_container:
            username_element = username_container.find('span', {'class': 'typography_heading-xxs__QKBS8'})
            username = username_element.text.strip() if username_element else "Username not found"

        reviews.append({
            'id': f'reviews-{index + 1}',
            'url': review_url,
            'img_src': img_src,
            'time': review_time,
            'title': review_title,
            'content': review_content,
            'username': username
        })

    # 封装成一个JSON对象
    combined_data = {
        'trustpilot_url': trustpilot_url,
        'grades_name': grades_name,
        'grades_img': grades_img,
        'rv_total_num': rv_total_num,
        'reviews': reviews
    }

    # 将JSON对象输出到控制台
    combined_data_json = json.dumps(combined_data, indent=4)

    # 预定格式
    pretype = {
        "dataId": "tp-youezpay2",
        "value": combined_data_json
    }

    response = requests.post(api_url, json=pretype)
    print("Response from server:", response.json())

# 根据规定时间进行爬取
def run_periodically(interval_hours):
    while True:
        fetch_trustpilot_reviews()
        print(f"Data fetched and sent to server. Next fetch in {interval_hours} hours.")
        time.sleep(interval_hours * 3600)  # 将小时转换为秒

if __name__ == "__main__":
    interval_hours = 0.5  # 设置每隔1小时执行一次
    # 使用线程来运行定时任务
    threading.Thread(target=run_periodically, args=(interval_hours,)).start()
