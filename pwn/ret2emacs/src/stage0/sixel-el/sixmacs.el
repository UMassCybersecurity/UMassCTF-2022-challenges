;; Author: Jakob L. Kreuze <https://jakob.space>

(defvar sixplayground-overlays '())

(defun sixplayground-make-overlay (start end data-or-function)
  (let* ((overlay (make-overlay (car match) (cadr match)))
         (data (if (stringp data-or-function)
                   data-or-function
                 (funcall data-or-function))))
    (overlay-put overlay 'display (create-image data 'pbm t))
    (push overlay sixplayground-overlays)))

(defun sixplayground-parse ()
  (save-excursion
    (set-buffer (get-buffer "*scratch*"))
    (dolist (overlay sixplayground-overlays)
      (delete-overlay overlay))
    (setq sixplayground-overlays '())
    (dolist (match (matches-in-buffer "P0;0;0q.*?\\\\"))
      (sixplayground-make-overlay (car match) (cdr match)
                                  (sixel-decode-string (buffer-substring (car match) (cadr match)))))))

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
      (reverse matches))))

(defun sixplayground-on-post-command (&rest args)
  (when (buffer-modified-p (get-buffer "*scratch*"))
    (sixplayground-parse)
    (set-buffer-modified-p nil)))
