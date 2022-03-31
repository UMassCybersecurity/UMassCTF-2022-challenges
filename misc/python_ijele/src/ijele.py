def main():
    print('wewe have aqhephukile benim bahasa codice. Unesi la palabra sapi in Pelekania')
    code = input('>>> ')
    if code.lower() == 'cow':
        print('Break out of this simple python jail! You are not allowed to use the words eval, exec, import, open, os, read, system, or write.')
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
