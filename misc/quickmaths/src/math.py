import random
# import time
import sys

def flag():
    print("UMASS{s3v3naten1n3}")
    sys.exit(0)


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

    try:
        if int(input()) == answer:
            print("Correct!")
            return True
        else:
            print("Incorrect.")
            return False
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    print("You must solve 1000 of these math problems that are outputted in the following format {number} {operation} {number} to get the flag. \nDivision is integer division using the // operator. \nThe input is being checked through python input() function. \nGood luck! \n")
    correct = 0
    numprobs = 1000 
    # start = time.time()
    for i in range(numprobs):
        if mathproblem():
            correct += 1
        # if time.time() - start >= 10:
        #     print("Timeout. You took too long.")
        #     sys.exit(0)
        #     break
    if correct == numprobs:
        flag()
    else:
        print("You didn't get all the problems correct. Try again.")
    sys.exit(0)
