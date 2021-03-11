# WATERs

<!-- 소개 -->
수경재배 시스템

<!-- 설치 방법 -->

### 파이썬 라이브러리 설치
* sudo pip3 install tendo
* sudo pip3 install paho-mqtt python-etcd
* sudo pip3 install unidecode
* sudo pip3 install sdnotify
* sudo pip3 install miflora
* sudo pip3 install bluepy
* sudo pip3 install colorama
* sudo pip3 install --upgrade psutil


### 자동 부팅 설정
sudo nano /etc/profile

마지막에 `/home/pi/autoStartup.sh` 추가

### crontab 설정
crontab -e
```
* * * * * /home/pi/WATERs/bin/update.sh
```
맨 아래에 추가

<!-- 설정 방법 -->
## Configuration

<!-- 사용 방법 -->
## Usage

<!-- 문제 해결 -->
## Troubleshooting

