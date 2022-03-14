from pwn import *

def formatcount(str):
	ind = 0
	for i in range(16):
		for j in range(16):
			print(str[ind],end='')
			ind+=1
		print()

def genfirst():
	global s
	s = b'0123456789:;<=>?'
	print('send:',s.decode('utf-8'))
	return s

def getbit(num, bit):
	return (num>>bit)&1

def arrtoint(arr):
	ans = 0
	for a in reversed(arr):
		ans *= 2
		ans += a
	return ans

def getx(str):
	global bestx, x, s
	for i in range(16):
		m = 20
		l = s[i]
		for j in range(16):
			ind = j+i*16
			c = str[ind]
			m = min(m, int(c,16))
		if m > bestx:
			bestx = m
			for j in range(4):
				x[j] = getbit(l,j)


def gety(str):
	global besty, y, s
	for i in range(16):
		m = 20
		r = s[i]
		for j in range(16):
			ind = i+j*16
			c = str[ind]
			m = min(m, int(c,16))
		if m > besty:
			besty = m
			for j in range(4):
				y[j] = getbit(r,j)

def lowersolve(str):
	global bestx,x,besty,y,firstx,firsty
	bestx = 0
	x = [0,0,0,0,0,0,0,0]
	besty = 0
	y = [0,0,0,0,0,0,0,0]
	getx(str)
	gety(str)
	lowerx = arrtoint(x)
	lowery = arrtoint(y)
	firstx = lowerx
	firsty = lowery

def getx2(str):
	global bestx, x, s, firstx, offshift
	for i in range(8):
		m = 20
		l = ((i+offshift)<<4)+firstx
		for j in range(8):
			ind = 8+j+i*16
			c = str[ind]
			m = min(m, int(c,16)-8)

		if m > bestx:
			bestx = m
			for j in range(7):
				x[j] = getbit(l,j)

def gety2(str):
	global besty, y, s, firsty, offshift

	for i in range(8):
		m = 20
		r = ((i+offshift)<<4)+firsty
		for j in range(8):
			ind = i+8+j*16
			c = str[ind]
			m = min(m, int(c,16)-8)
		if m > besty:
			besty = m
			for j in range(7):
				y[j] = getbit(r,j)

def uppersolve(str):
	global bestx, x, besty,y
	bestx = 0
	x = [0,0,0,0,0,0,0,0]
	besty = 0
	y = [0,0,0,0,0,0,0,0]
	getx2(str)
	gety2(str)
	upperx = arrtoint(x)
	uppery = arrtoint(y)
	if bestx < 7:
		upperx += 128
	if besty < 7:
		uppery += 128

	return (upperx, uppery)

# inp = input('count string:')

def genstring():
	global offshift, firstx, firsty
	nexts = ''
	for i in range(offshift, offshift+8):
		nextord = (i<<4)+firstx
		nexts += chr(nextord)
	for i in range(offshift, offshift+8):
		nextord = (i<<4)+firsty
		nexts += chr(nextord)
	print('send:',nexts)
	return nexts.encode('utf-8')



offshift = 0

r = remote('misc1.utctf.live', 5000)

for i in range(100):
	print(r.recvline().strip().decode('utf-8'))
	r.recvline()
	genfirst()
	r.send(s)
	print('Send: ',end='')
	print(s.decode('utf-8'))

	inp = r.recvuntil(b'\n').strip().decode('utf-8')
	formatcount(inp)
	print()

	r.recv()
	lowersolve(inp)

	nxs = genstring()
	r.send(nxs)
	print('Send: ',end='')
	print(nxs.decode('utf-8'))

	inp = r.recvuntil(b'\n').strip().decode('utf-8')
	formatcount(inp)
	print()

	ansx, ansy = uppersolve(inp)

	r.recvline()
	r.recvline()
	r.sendline(str(ansx))
	r.recvline()
	r.sendline(str(ansy))

	print('Ans: k1=',ansx,' k2=',ansy,sep='',end='\n\n')

r.interactive()
