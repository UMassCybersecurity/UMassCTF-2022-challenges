This is a custom-made archive type embedded in a jpeg file, try guessing the key
and extracting the content, which includes the flag.

The archive is located at the end of the jpeg, after `FF D9`. It shall begin
with `MyrA`. Seperate the archive bytes. If we `strings` the file,
we can see 2 possible files within it. The archive data contains a structure
of Table-of-Content (TOC) and data. The TOC contains data's location and size,
so we can extract files by hand, using Python, or using Kaitai Struct. One file
is similar to the image at the beginning, and the other file contains the flag.