import sys
import time
import os
#import signal
#import subprocess

def jailbreakattempt(allowedchars):
    print('Input whatever you wish to try to break out of this game with in the following input.')
    print('Here are the characters you are allowed to use: {}'.format(str(sorted(allowedchars))[1:-1]))
    try:
        text = input('>>> ')
    except KeyboardInterrupt:
        #print('\n I GOTCHA BITCH')
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
    ----------------------------------------- JeopardyV2! -------------------------------------------
    Sound Familiar:  Cybersecurity Now:  Cybersecurity History:  Computer Programming:  Miscellaneous:
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
                gbqsprinted += "      "
            elif j == 0:
                gbqsprinted += "          "
            elif j == 1:
                gbqsprinted += "              "
            elif j == 2:
                gbqsprinted += "                    "
            elif j == 3:
                gbqsprinted += "                    "
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

    a1 = {'chars': ['('], 'points': 100, 'question': 'This technology that can be used to create fake events with real images, like faces, is a serious concern for future cybersecurity.', 'answer': ['deep fake', 'deepfake', 'deepfakes', 'DeepFake'],
          'answered': False}
    a2 = {'chars': ['{'], 'points': 200, 'question': 'If there are 6 apples and you take away 4, how many apples do you have?',
          'answer': ['4', 'four'], 'answered': False}
    a3 = {'chars': ['}'], 'points': 300, 'question': 'What was the keyboard layout used to decode instructions given to the player in a miscellaneous challenge in last years CTF? (hint: it is not qwerty)',
          'answer': ['dvorak', 'Dvorak'], 'answered': False}
    a4 = {'chars': ['x'], 'points': 400, 'question': 'Dogs are often used to aid police forces with many tasks. This special kind of dog is especially useful in helping sniff out Cybersecurity-related crimes (like the Subway Scandal)',
          'answer': ['electronic sniffing dog', 'electronics sniffing dog', 'electronic dog', 'electronics', 'electronic sniffing', 'electronic-sniffing dog', 'electronics-sniffing dog'], 'answered': False}
    a5 = {'chars': ['s', 't', 'u', 'v'], 'points': 500, 'question': 'The creator of this challenge is in charge of getting industry professionals to talk to the UMass Cybersecurity Club. Once, there was an industry talk from Oracle where a password was leaked but the presentor was fine with it. What was this password?', 'answer': ['gsh1ggcjhimhy0xamn'], 'answered': False}

    b1 = {'chars': [':'], 'points': 100,
          'question': 'What is the name of the Java library that had a zero-day vulnerability which caused a massive response worldwide in December of 2021?',
          'answer': ['log4j', 'apache log4j'], 'answered': False}
    b2 = {'chars': [')'], 'points': 200,
          'question': 'What was the name given to the critical security vulnerability in June/July 2021 allowing for remote code execution and priviliege escalation having to do with a Windows printing service?',
          'answer': ['printnightmare', 'print nightmare'], 'answered': False}
    b3 = {'chars': ['+'], 'points': 300, 'question': 'What is the CVE for which a very popular web browser had to release a patch for, due to a zero-day, just last week? (answer is "CVE-####-####")',
          'answer': ['cve-2022-1096'], 'answered': False}
    b4 = {'chars': ['_', '<'], 'points': 400, 'question': 'Recently, one of the richest men in the world provided free internet service for all Ukrainians through his satellite Internet company called', 'answer': ['starlink', 'star link'], 'answered': False}
    b5 = {'chars': ['p', 'q'], 'points': 500,
          'question': 'What global "day" involving cybersecurity happened this last Thursday relating to protecting your data?',
          'answer': ['world backup day', 'backup day', 'backup-day', 'world backup day 2022', 'global backup day'], 'answered': False}

    c1 = {'chars': ['%'], 'points': 100, 'question': 'Famous ruler who has a cipher named after them',
          'answer': ['caesar', 'julius caesar'], 'answered': False}
    c2 = {'chars': ['.'], 'points': 200, 'question': 'The first real computer virus was dubbed the',
          'answer': ['the creeper', 'creeper'], 'answered': False}
    c3 = {'chars': ['c'], 'points': 300, 'question': 'What is considered the first computer worm that was originally designed as anti-virus software?',
          'answer': ['the reaper', 'reaper'], 'answered': False}
    c4 = {'chars': ['1'], 'points': 400, 'question': 'Give the most notable nickname for the man who hacked the New York Times in 2002 by adding himself to the list of expert sources among other things', 'answer': ['homesless', 'homeless hacker', 'the homeless hacker'], 'answered': False}
    c5 = {'chars': ['j', 'k', 'l'], 'points': 500, 'question': 'Name the woman who was one of the first and most notable of all social engineers who started her hacking career in Los Angeles', 'answer': ['susan headley', 'susy thunder', 'susan thunder'], 'answered': False}

    d1 = {'chars': ["'"], 'points': 100, 'question': 'What was the first ever physical computer bug?', 'answer': ['moth', 'a moth'], 'answered': False}
    d2 = {'chars': ['e'], 'points': 200, 'question': 'What was the first proposed computer in the 1800s going to run off of for a power source?',
          'answer': ['steam', 'steam-powered'], 'answered': False}
    d3 = {'chars': ['['], 'points': 300, 'question': 'The first ever computer game made the creators this many dollars', 'answer': ['zero', '0'], 'answered': False}
    d4 = {'chars': [']'], 'points': 400, 'question': 'As of 2020, you could not represent this value as an integer in any coding language', 'answer': ['inf', 'infinity', 'negative infinity'], 'answered': False}
    d5 = {'chars': ['m', 'n', 'o'], 'points': 500, 'question': 'What was the mathematical nickname given to the first computer programmers mother by said programmers father?', 'answer': ['princess of parallelograms', 'the princess of parallelograms'], 'answered': False}

    e1 = {'chars': ['`'], 'points': 100, 'question': 'You can only win prizes in this CTF if you are a _______', 'answer': ['student', 'university student', 'in college', 'students'], 'answered': False}
    e2 = {'chars': ['r'], 'points': 200, 'question': 'Name a sponsor of this CTF', 'answer': ['gcp', 'google cloud', 'akamai', 'htb', 'hackthebox', 'offensive security', 'offensivesecurity', 'cics', 'umass amherst cics', 'mcics', 'umass', 'umass amherst', 'umass cics', 'umass mcics', 'atc', 'american tower', 'american tower corporation', 'tryhackme', 'thm'], 'answered': False}
    e3 = {'chars': ['h'], 'points': 300, 'question': 'What three word phrase would the newest host of Jeopardy, Ken Jennings, say at the end of the show during his first few months of hosting?', 'answer': ['thank you alex'], 'answered': False}
    e4 = {'chars': [',', '~'], 'points': 400, 'question': 'What year was UMassCTF first hosted?', 'answer': ['2020'], 'answered': False}
    e5 = {'chars': ['a', 'b', 'd', 'f', 'g', 'i', 'w', 'y', 'z'], 'points': 500, 'question': 'There is a story that if you find the frog on top of this object, which is carved as part of the main facade of a very old university in Spain, you will pass all your exams', 'answer': ['skull', 'head', 'skulls', 'a skull', ], 'answered': False}

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
        #print('\n I GOTCHA BITCH')
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
                #print('\n I GOTCHA BITCH')
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
            if category == 'sound familiar':
                currentquestion = gameboardboolean[arrayrow][0]
            elif category == 'cybersecurity now':
                currentquestion = gameboardboolean[arrayrow][1]
            elif category == 'cybersecurity history':
                currentquestion = gameboardboolean[arrayrow][2]
            elif category == 'computer programming':
                currentquestion = gameboardboolean[arrayrow][3]
            elif category == 'miscellaneous':
                #if questionpick.split(" ")[-1] == '10000':
                #    currentquestion = gameboardboolean[4][4]
                #else:
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
                    #print('ASDIJASODAOJSDOIJASDOIJADSOAOSJD')
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
                    #print('\n I GOTCHA BITCH')
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
    #signal.signal(signal.SIGINT, saveourmoney)
    #signal.signal(signal.SIGTERM, saveourmoney)
    main()
