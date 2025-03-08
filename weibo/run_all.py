import subprocess

# 依次运行四个 Python 文件
subprocess.run(['python', 'resou_rank_url_title_spider.py'])
subprocess.run(['python', 'postID_spider.py'])
subprocess.run(['python', 'poster_spider.py'])
subprocess.run(['python', 'commend_spider.py'])