import random
import time

def flag():
    print("UMASS{OOGABOOGA}")


def mathproblem():
    a = random.randint(-100, 100)
    b = random.randint(-100, 100) 
    op = random.randint(0, 3)
    operation = ""
    
    if op == 0:
        answer = a + b
        operation = "+"
    elif op == 1:
        answer = a - b
        operation = "-"
    elif op == 2:
        answer = a * b
        operation = "*"
    else:
        answer = a // b
        operation = "//"
    print("{} {} {}".format(a, operation, b))

    if int(input()) == answer:
        print("correct!")
        return True
    else:
        return False

if __name__ == '__main__':
    print("You must solve 1000 of these math problems that are outputted in the following format {number} {operation} {number} within 10 seconds to get the flag. Good luck! \n")
    correct = 0
    numprobs = 2
    start = time.time()
    for i in range(numprobs):
        if mathproblem():
            correct += 1
        if time.time() - start >= 10:
            print("Timeout. You took too long.")
            break
    if correct == numprobs:
        flag()
