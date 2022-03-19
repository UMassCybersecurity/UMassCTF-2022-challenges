# babyvm

Some cursory reverse engineering and familiarity with popular computer science
will lead to the conclusion that this is a JIT for
[Brainfuck](https://en.wikipedia.org/wiki/Brainfuck). While I expect nearly
everyone to be familiar with Brainfuck, I don't think it's unreasonable to
assume one could come up with the solution below without knowing that the
bytecode format is Brainfuck with a different character set.

Reverse engineering the code itself is futile. Possible, perhaps, but there are
better solutions. My approach was to build a visualizer for the memory of the
program to get an idea of what was going on. We know that the flag is going to
start with "UMASS{", so we can compare the behavior when the program is run on
"UMASS{\x00..." versus when it is run on "\x00\x00\x00...". 

There is one cell (at index `1`) which starts as `1` in the beginning, and is
changed to `0` later in the program execution. This change occurs later for the
"UMASS{\x00..." input, so we can infer that it is related to whether the input
is correct. Hence, we can determine the flag character-by-character by
determining which choice of `FLAG[i]` increases the steps taken before the cell
at index `1` is decremented.

The way I did this was to re-write the Brainfuck interpreter in Python, add my
own introspection to count the number of steps before `memory[1]` is
decremented, and find the input which causes that input to deviate from the rest
(when we normalize against `ord(char)`, which is necessary because of how
equality is performed by this Brainfuck program). Running the `solver.py` script...

```
jakob@Epsilon ~ $ python Code/UMassCTF-2022-challenges/rev/babyvm/solution/solver.py 
Found differences: [520, 520, 520, 520, 520, 520, 520, 520, 520]
Found normalizer: 520
Found values: [3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160]
Found differences: [520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520]
Found normalizer: 520
Found values: [3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928, 3247928]
Found differences: [520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 520, 1434, 374, 520, 520, 520, 520]
Found normalizer: 520
Found values: [3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3247160, 3248074, 3247928, 3247928, 3247928, 3247928, 3247928]
Found letter: U
Found differences: [544, 544, 544, 544, 544, 544, 544, 544, 544]
...
Found normalizer: 1816
Found values: [8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141]
Found differences: [1816, 0, 1816, 1816, 1816, 1816, 49032, 1816, 2059, 2341]
Found normalizer: 1816
Found values: [8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726141, 8726384, 8726909]
Found letter: }
[85, 77, 65, 83, 83, 123, 72, 48, 80, 101, 95, 49, 95, 78, 69, 86, 101, 114, 95, 104, 52, 118, 101, 95, 55, 48, 95, 53, 69, 69, 95, 55, 72, 49, 122, 95, 69, 53, 48, 76, 52, 110, 71, 95, 69, 86, 101, 82, 95, 52, 71, 52, 49, 78, 125]
jakob@Epsilon ~ $ python
Python 3.9.10 (main, Mar  5 2022, 22:52:09) 
[GCC 11.2.1 20220115] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> bytes([85, 77, 65, 83, 83, 123, 72, 48, 80, 101, 95, 49, 95, 78, 69, 86, 101, 114, 95, 104, 52, 118, 101, 95, 55, 48, 95, 53, 69, 69, 95, 55, 72, 49, 122, 95, 69, 53, 48, 76, 52, 110, 71, 95, 69, 86, 101, 82, 95, 52, 71, 52, 49, 78, 125])
b'UMASS{H0Pe_1_NEVer_h4ve_70_5EE_7H1z_E50L4nG_EVeR_4G41N}'
jakob@Epsilon ~/Code/UMassCTF-2022-challenges/rev/babyvm $ src/target/debug/babyvm 
UMASS{H0Pe_1_NEVer_h4ve_70_5EE_7H1z_E50L4nG_EVeR_4G41N}
*
```
