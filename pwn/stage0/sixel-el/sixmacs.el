(defvar sixplayground-overlays '())

(defvar sixplayground-test-image
        "P1
# Created by GIMP version 2.10.30 PNM plug-in
32 32
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000001100000000000000000
0000001000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000001100000000000100000
0000000000000100000000000010000000000000000001000000000000100000000000
0000000100000000000010000000000000000000110000000000100000000000000000
0000110000000100000000000000000000000011000001000000000000000000000000
0011111000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000")

(defun sixplayground-parse ()
  (save-excursion
    (set-buffer (get-buffer "*scratch*"))
    (dolist (overlay sixplayground-overlays)
      (delete-overlay overlay))
    (setq sixplayground-overlays '())
    (dolist (match (matches-in-buffer "P0;0;0q.*?\\\\"))
      (let ((overlay (make-overlay (car match) (cadr match))))
        ;; (overlay-put overlay 'invisible t)
        (overlay-put overlay 'display (create-image sixplayground-test-image 'pbm t))
        (push overlay sixplayground-overlays)))))

(defun matches-in-buffer (regexp &optional buffer)
  "return a list of matches of REGEXP in BUFFER or the current buffer if not given."
  (let ((matches))
    (save-match-data
      (save-excursion
        (with-current-buffer (or buffer (current-buffer))
          (save-restriction
            (widen)
            (goto-char 1)
            (while (search-forward-regexp regexp nil t 1)
              (push (list (match-beginning 0) (match-end 0)) matches)))))
      matches)))

(defun sixplayground-on-post-command ()
  (when (buffer-modified-p (get-buffer "*scratch*"))
    (sixplayground-parse)
    (set-buffer-modified-p nil)))

(add-hook 'post-command-hook #'sixplayground-on-post-command)
(progn (remove-hook 'post-command-hook #'sixplayground-on-post-command)
       (dolist (overlay sixplayground-overlays)
         (delete-overlay overlay)))

(string-match "P0;0;0q.*?\\\\" "P0;0;0q\"1;1;32;32#0;2;0;0;0#1;2;100;0;0#1!32~-!32~-!10~|!6~}}!13~$#0!10?A!6?@@-#1!9~Fv!11~F!9~$#0!9?wG!11?w-#1!9~}||zzvv!5nr{!9~$#0!9?@AACCGG!5OKB-#1!32B-\\")
