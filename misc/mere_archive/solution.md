The archive is located at the end of the jpeg, after `DD F9`. It shall begin
with `MyrA`. Extract the archive to a seperate file. If we `strings` the file,
we can see 2 possible files within it. The archive data contains a structure
of Table-of-Content (TOC) and data, which can be visualized using Kaitai
Struct. The TOC contains data's location and size, so we can extract of file
by hand, using Python, or using Kaitai Struct API. One file is similar
to the image at the beginning, and the other file contains the flag.