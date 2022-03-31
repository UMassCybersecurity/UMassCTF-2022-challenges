One simple solution is run the source code through C/C++ compiler preprocessor:
`clang -C -E test.tino.cpp`. Scroll down to the bottom and you will receive the
source code after applying all `#define`. Checking through the source code,
there's a bug during printing, which the program should print on even index
rather than odd index.
One hard way is to compile to binary and reverse it.