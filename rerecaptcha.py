from bs4 import BeautifulSoup
from PIL import Image, ImageFilter
import requests
from io import BytesIO
import base64
import pytesseract
import re

link = 'http://web1.utctf.live:7132/'
bestscore=int(input('best score: '))
bestcookie=input('best cookie: ')
cookie = {bestscore:{'session':bestcookie}}

# Step 1 - Training
# Get 1,000 "training" images to figure out the common background
for i in range(1000):
	if (i%10==0): print(i)
	r = requests.get(link)
	respcont = r.content
	respcookie = r.cookies
	soup = BeautifulSoup(respcont,"html.parser")
	captcha = soup.findAll('img')[0]['src'][23:]
	captchaim = Image.open(BytesIO(base64.b64decode(captcha)))
	captchaim.save("captcha/training"+str(i)+".png")



# Step 2 - Construction
# Get the most common pixels at each position
pixel = [[{} for j in range(150)] for i in range(500)]
for i in range(1000):
	if (i%10 == 0): print(i)
	captchapath = "captcha/training"+str(i)+".png"
	trainingcaptcha = Image.open(captchapath)
	pixels = trainingcaptcha.load()
	for r in range(500):
		for c in range(150):
			p = pixels[r,c]
			if p in pixel[r][c]:
				pixel[r][c][p]+=1
			else:
				pixel[r][c][p]=1

construct = Image.new('RGB', (500, 150))
constructpixels = construct.load()

for r in range(500):
	for c in range(150):
		most = 0
		for p in pixel[r][c]:
			count = pixel[r][c][p]
			if count > most:
				most = count
				constructpixels[r,c] = p

construct.save("captcha/background.png")
construct.show()


# Step 3 - Solving
construct = Image.open("captcha/background.png")
constructpixels = construct.load()
human = ''

while bestscore < 1000:
	sess = requests.Session()

	# get the captcha
	r = sess.get(link, cookies=cookie[bestscore])
	respcont = r.content
	soup = BeautifulSoup(respcont,"html.parser")
	score = int(soup.findAll('p')[0].getText().split()[3])
	bestscore = score
	captcha = soup.findAll('img')[0]['src'][23:]
	captchaim = Image.open(BytesIO(base64.b64decode(captcha)))
	captchaimpixels = captchaim.load()
	
	# get the difference between this and base background
	difference = Image.new('RGB', (500, 150))
	makediff = difference.load()
	for r in range(500):
		for c in range(150):
			cop = constructpixels[r,c]
			cap = captchaimpixels[r,c]
			if cop != cap:
				makediff[r,c] = (0,0,0)
				# some manual patches
				if r >= 17 and r <= 19 and c >= 53 and c <= 99:
					makediff[r,c] = (255,255,255)
				if r >= 20 and r <= 25 and c >= 33 and c <= 99:
					makediff[r,c] = (255,255,255)
				if r >= 46 and r <= 50 and c >= 54 and c <= 66:
					makediff[r,c] = (255,255,255)
				if r >= 31 and r <= 53 and c >= 94 and c <= 99:
					makediff[r,c] = (255,255,255)
				if r >= 91 and r <= 111 and c >= 94 and c <= 99:
					makediff[r,c] = (255,255,255)

			else:
				makediff[r,c] = (255,255,255)
				# some manual patches
				if r >= 17 and r <= 19 and c >= 53 and c <= 99:
					makediff[r,c] = (0,0,0)
				if r >= 20 and r <= 25 and c >= 33 and c <= 99:
					makediff[r,c] = (0,0,0)
				if r >= 46 and r <= 50 and c >= 54 and c <= 66:
					makediff[r,c] = (255,255,255)
				if r >= 31 and r <= 53 and c >= 94 and c <= 99:
					makediff[r,c] = (0,0,0)
				if r >= 91 and r <= 111 and c >= 94 and c <= 99:
					makediff[r,c] = (0,0,0)

	difference.filter(ImageFilter.SMOOTH_MORE)

	# submit captcha
	captchatext = pytesseract.image_to_string(difference, config='--oem 1 --psm 13')
	captchatext = re.sub(r'[^A-Za-z0-9]+', '', captchatext)
	postdata = {'solution':captchatext}
	r = sess.post(link, data=postdata)
	
	# parse response
	respcont = r.content
	respcookie = r.cookies['session']
	soup = BeautifulSoup(respcont,"html.parser")
	score = int(soup.findAll('p')[0].getText().split()[3])

	if score > bestscore:
		# update bestscore
		bestscore = score
		cookie[score] = {'session':respcookie}
		print(score,respcookie)
	else:
		# backtrack
		bestscore -= 1
