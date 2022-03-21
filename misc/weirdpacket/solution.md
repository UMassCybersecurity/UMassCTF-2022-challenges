This is a Fax (v.29) transmission, so some signal processing experience helps in
solving this challenge. With some modifications to ignore parts of the protocol,
a decent [softmodem](https://github.com/randyrossi/fisher-modem) is capable of
reading out the document. There isn't much noise in the audio file.

The document that's spat out isn't regular text, though. It's binary data,
encoded as pixels. The binary data is, however, fairly easy to parse. It's a
HTTP packet with the flag in the header.

`UMASS{BrUH_7hA72_Ip_0V3r_fAX}`
