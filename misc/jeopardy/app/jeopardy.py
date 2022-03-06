import sys
import time
import os
import signal
import subprocess

def jailbreakattempt(allowedchars):
    print('Input whatever you wish to try to break out of this game with in the following input.')
    print('Here are the characters you are allowed to use: {}'.format(str(sorted(allowedchars))[1:-1]))
    try:
        text = input('>>> ')
    except KeyboardInterrupt:
        print('\n I GOTCHA BITCH')
        sys.exit(0)
    for char in text:
        #print(char)
        #print(allowedchars)
        if char not in allowedchars:
            print('You entered a character you are not allowed to use. Go answer more questions or rerun the game.')
            return
    try:
        exec(text)
    except:
        print('Your input threw an exception. Try something different.')


def displaygb(gameboardboolean):
    gbheader = """
    ----------------------------------------- Jeopardy! -----------------------------------------
    UMass:  Cybersecurity Now:  Cybersecurity Yesterday:  Cybersecurity Tomorrow:  Miscellaneous:
    """
    gbqs = [
    ['','','','',''],
    ['','','','',''],
    ['','','','',''],
    ['','','','',''],
    ['','','','','']
     ]

    gbqsprinted = ""

    for i in range(5):
        for j in range(5):
            if j == 0 and i == 0:
                gbqsprinted += " "
            elif j == 0:
                gbqsprinted += "     "
            elif j == 1:
                gbqsprinted += "           "
            elif j == 2:
                gbqsprinted += "                     "
            elif j == 3:
                gbqsprinted += "                      "
            elif j == 4:
                gbqsprinted += "                 "
            if gameboardboolean[i][j]['answered'] is False:
                gbqs[i][j] = gameboardboolean[i][j]['points']
                gbqsprinted += str(gameboardboolean[i][j]['points'])
            else:
                gbqsprinted += "   "
        gbqsprinted += '\n'

    print(gbheader + gbqsprinted)

def main():
    allowedchars = [' ']
    
    #allowedchars = [chr(i) for i in range(128)]

    a1 = {'chars': ['('], 'points': 100, 'question': 'What is the name of the mascot of UMass?', 'answer': ['sam', 'sam the minuteman'],
          'answered': False}
    a2 = {'chars': ['{'], 'points': 200, 'question': 'What is UMass most famously known for being #1 for?',
          'answer': ['dining', 'food', 'dining program'], 'answered': False}
    a3 = {'chars': ['}'], 'points': 300, 'question': 'What dining hall is hard-serve ice cream served at on campus everyday?',
          'answer': ['frank', 'franklin', 'franklin dining commons'], 'answered': False}
    a4 = {'chars': ['x'], 'points': 400, 'question': 'Where was the old honors college located?',
          'answer': ['orchard hill', 'ohill', 'orchard hill area', 'orchard hill residential area'], 'answered': False}
    a5 = {'chars': ['s', 't', 'u', 'v'], 'points': 500, 'question': 'This flag was raised from a dorm in the central housing area in the 90s due to unrest from the residents', 'answer': ['jolly roger', 'jolly roger flag'], 'answered': False}

    b1 = {'chars': [':'], 'points': 100,
          'question': 'According to UMaryland Professor, a hacker attacks computers on average every ___ seconds?',
          'answer': ['39'], 'answered': False}
    b2 = {'chars': [')'], 'points': 200,
          'question': 'University of Michigan researchers controlled a Google Home from 230 feet away with what?',
          'answer': ['laser', 'lasers'], 'answered': False}
    b3 = {'chars': ['+'], 'points': 300, 'question': 'Band that was recently threatened to have unreleased music released unless they pay the hackers money',
          'answer': ['radiohead', 'radio head'], 'answered': False}
    b4 = {'chars': ['_', '<'], 'points': 400, 'question': 'This company recently had their source code accessed in a huge breach', 'answer': ['microsoft', 'windows'], 'answered': False}
    b5 = {'chars': ['p', 'q'], 'points': 500,
          'question': 'What is a fairly new way to find electronics that law enforcement are using, i.e. Subway scandal',
          'answer': ['electronic sniffing dog', 'electronic sniffing dogs', 'dogs', 'dog'], 'answered': False}

    c1 = {'chars': ['%'], 'points': 100, 'question': 'Nickname of one of the first "hackers" that is a cereal brand',
          'answer': ['captain crunch'], 'answered': False}
    c2 = {'chars': ['1'], 'points': 200, 'question': 'Movie where tic-tac-toe used to save the world?',
          'answer': ['wargames', 'war games'], 'answered': False}
    c3 = {'chars': ['c'], 'points': 300, 'question': 'Country that US and Israeli has made multiple worms and malware against?',
          'answer': ['iran'], 'answered': False}
    c4 = {'chars': ['.'], 'points': 400, 'question': 'The first real use of cybersecurity against a virus was a program called the ___?', 'answer': ['the reaper', 'reaper'], 'answered': False}
    c5 = {'chars': ['j', 'k', 'l'], 'points': 500, 'question': 'DoD wrote this during the cold war', 'answer': ['orange book', 'the orange book'], 'answered': False}

    d1 = {'chars': ["'"], 'points': 100, 'question': 'This type of computing that has much promise for the future poses a great threat to encryption schemes commonly used today', 'answer': ['quantum', 'quantum computing'], 'answered': False}
    d2 = {'chars': ['e'], 'points': 200, 'question': 'This year will be the next y2k thanks to some data types',
          'answer': ['2038', 'year 2038'], 'answered': False}
    d3 = {'chars': ['['], 'points': 300, 'question': 'Said to be the number 1 risk or threat in cybersecurity for the foreseeable future', 'answer': ['human nature', 'humans', 'people', 'human'], 'answered': False}
    d4 = {'chars': [']'], 'points': 400, 'question': 'This architecture of CPUs seems to have many benefits but has repeatedly had vulnerabilities found in it after major releases of them', 'answer': ['arm', 'arm processors'], 'answered': False}
    d5 = {'chars': ['m', 'n', 'o'], 'points': 500, 'question': 'This technology that can be used to create fake events with real images is a serious concern for future cybersecurity', 'answer': ['deepfake', 'deepfakes'], 'answered': False}

    e1 = {'chars': ['`'], 'points': 100, 'question': 'Name a sponsor of UMassCTF', 'answer': ['google cloud', 'google dsc', 'hackthebox', 'akamai', 'tryhackme'], 'answered': False}
    e2 = {'chars': ['r'], 'points': 200, 'question': 'This was the most popular OS that was used in 2020', 'answer': ['ios'], 'answered': False}
    e3 = {'chars': ['h'], 'points': 300, 'question': 'The answer to the life, universe, everything? In binary, of course.', 'answer': ['101010'], 'answered': False}
    e4 = {'chars': [',', '~'], 'points': 400, 'question': 'If there are 6 apples and you take away 4, how many do you have?', 'answer': ['4'], 'answered': False}
    e5 = {'chars': ['a', 'b', 'd', 'f', 'g', 'i', 'w', 'y', 'z'], 'points': 10000, 'question': 'The UMass Cybersecurity club holds many talks from a wide variety of industry '
                                       'professionals in the tech scene. One such company may have leaked a password to '
                                       'something they were demoing during their presentation but did not care. What was'
                                       ' the password displayed on the screen?', 'answer': ['gsh1ggcjhimhy0xamn'], 'answered': False}

    gameboardboolean = [
        [a1, b1, c1, d1, e1],
        [a2, b2, c2, d2, e2],
        [a3, b3, c3, d3, e3],
        [a4, b4, c4, d4, e4],
        [a5, b5, c5, d5, e5]
    ]

    displaygb(gameboardboolean)

    print('Type "ready" when you are ready to play!')
    try:
        userready = input()
    except KeyboardInterrupt:
        print('\n I GOTCHA BITCH')
        sys.exit(0)
    if userready != 'ready':
        print('Terminating program.')
        sys.exit(0)

    totalquestions = 25
    exitprogram = 0
    while totalquestions >= 1:
        # try:
            print('\nPick a category and dollar amount in the format of "category dollar amount" with no dollar sign from the board below')
            print('or type "jailbreak" to attempt to breakout of the game.')
            displaygb(gameboardboolean)
            try:
                questionpick = input().lower()
            except KeyboardInterrupt:
                print('\n I GOTCHA BITCH')
                sys.exit(0)
            if questionpick == 'exit':
                print('Terminating program now')
                exitprogram = 1
                break
            if questionpick == 'jailbreak':
                jailbreakattempt(allowedchars)
                print("\nYou are back in the game loop. I hope it wasn't too easy...")
                continue
            if len(questionpick.split(" ")) < 2 or not questionpick.split(" ")[-1].isdigit():
                print('Please provide a category and dollar amount')
                continue
            category = ""
            for i in questionpick.split(" ")[0:-1]:
                category += i + " "
            category = category[0:-1]
            dollaramount = questionpick.split(" ")[-1]
            if int(dollaramount) != 100 and int(dollaramount) != 200 and int(dollaramount) != 300 and int(dollaramount) != 400 and int(dollaramount) != 500 and int(dollaramount) != 10000:
                print('Provide a valid dollar amount')
                continue
            arrayrow = int((int(questionpick.split(" ")[-1]) / 100) - 1)
            if category == 'umass':
                currentquestion = gameboardboolean[arrayrow][0]
            elif category == 'cybersecurity now':
                currentquestion = gameboardboolean[arrayrow][1]
            elif category == 'cybersecurity yesterday':
                currentquestion = gameboardboolean[arrayrow][2]
            elif category == 'cybersecurity tomorrow':
                currentquestion = gameboardboolean[arrayrow][3]
            elif category == 'miscellaneous':
                if questionpick.split(" ")[-1] == '10000':
                    currentquestion = gameboardboolean[4][4]
                else:
                    currentquestion = gameboardboolean[arrayrow][4]
            else:
                print('Not a valid category.')
                continue

            if currentquestion['answered'] is True:
                print('That question has already been answered.')
                continue
            else:
                print(currentquestion['question'])
                print('Your answer:')
                try:
                    useranswer = input()
                except KeyboardInterrupt:
                    print('ASDIJASODAOJSDOIJASDOIJADSOAOSJD')
                    sys.exit(0)
                currentquestion['answered'] = True
                if str(useranswer).lower() in currentquestion['answer']:
                    print('Correct! You have been awarded the following characters: {}'.format(str(currentquestion['chars'])[1:-1]))
                    for i in currentquestion['chars']:
                        allowedchars.append(i)
                else:
                    print('No, sorry. If you wish to try again you will have to restart the game entirely.')
                totalquestions -= 1
                time.sleep(2)
        # except:
            # print("An error occurred. Play the game as it was meant to be played, please :)")

    if exitprogram != 1:
        print('You have now attempted to answer all the questions. You can either exit this game by typing "exit" or continually attempt to jailbreak.')
        while True:
            # try:
                try:
                    finished = input()
                except KeyboardInterrupt:
                    print('\n I GOTCHA BITCH')
                    sys.exit(0)
                if finished == 'jailbreak':
                    jailbreakattempt(allowedchars)
                elif finished == 'exit':
                    print('Exiting now')
                    break
                else:
                    print('Invalid argument passed. Either type "jailbreak" or restart the game.')
            # except:
                # print('An error has occurred. Play the game it was meant to be played, please :)')


def saveourmoney(signum, frame):
    try:
        if raw_input("\nQuit jeopardy? (y/n)> ").lower().startswith('n'):
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nQuitting now...")
        sys.exit(0)


if __name__ == '__main__':
    print('Welcome to python jail-pardy! Each correctly answered question grants you characters which you can use try to break out of this game with to get the flag.')
    print('When you answer a question correctly, the game will tell you which characters have been unlocked.')
    print('To attempt to breakout, instead of picking a question, type the word "jailbreak" instead.')
    signal.signal(signal.SIGINT, saveourmoney)
    signal.signal(signal.SIGTERM, saveourmoney)
    main()
