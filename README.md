# Simple-Cloud-Analytics-Service
1062-LSA
> 簡易雲端數據服務

![概念圖](https://i.imgur.com/YzJQHJY.png)

# Example

![K-means](https://i.imgur.com/j5pW0o0.png)

# 設置說明
1.將 uwsgi9000.ini 放置於 /etc/  
2.於worker.py 設置 hostIP、serverIP

# 執行
web-server:
> python3 runserver.py

worker:
> python3 worker.py
