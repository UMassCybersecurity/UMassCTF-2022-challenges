(save-excursion
  (set-buffer "test2.sixel")
  (insert image-test-data))

(defun fake-module-reload (module)
  (interactive "fReload Module file: ")
  (let ((tmpfile (make-temp-file
                  (file-name-nondirectory module) nil module-file-suffix)))
    (copy-file module tmpfile t)
    (module-load tmpfile)))

(fake-module-reload "/home/jakob/emacs-sixel/sixmacs.so")
(fake-module-reload "/home/jakob/Code/emacs-libvterm/vterm-module.so")

(defvar image-test-data
  (save-excursion
    (set-buffer "test.sixel")
    (sixel-decode-string (buffer-substring 1 (buffer-size)))))

(insert-image (create-image image-test-data 'pbm t))


