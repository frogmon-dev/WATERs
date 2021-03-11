# -*- coding: utf-8 -*- 

# 중복 실행 방지
from tendo import singleton
try:
	me = singleton.SingleInstance()
except :
	print("another process running!")
	exit()
	
#프로그램 시작
from frogmon.uFlowerCare import FLOWERCARE

print('')
print('--------------------------------------------------')
print('**  Welcome to FROGMON corp.')
print("**  Let's make it together")
print("**  ")

FC = FLOWERCARE()
FC.atOnce()