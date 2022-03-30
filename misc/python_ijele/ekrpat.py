def main():
	print('Frg-k. xprt.b mf jre.! >ojal. ,cydrgy yd. d.nl ru .kanw .q.jw cmlrpyw rl.bw row p.aew ofoy.mw abe ,pcy.v ')
	code = input('>>> ')
	if code == 'dvorak':
		text = input('>>> ')
		for keyword in ['eval', 'exec', 'import', 'open', 'os', 'read', 'system', 'write']:
			if keyword in text:
				print('Play by the rules!!! Try again.')
				return
			else:
				exec(text)
	else:
		print('Wrong code to break out. Sorry, try again!')

if __name__ == "__main__":
	main()
