#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include <emacs-module.h>
#include <sixel/sixel.h>

int plugin_is_GPL_compatible;

void panic(emacs_env *ENV, char *message)
{
		emacs_value message_object = ENV->make_string(ENV, message, strlen(message));
		emacs_value symbol = ENV->intern(ENV, "sixel-decode-string");
		emacs_value args[] = {symbol, message_object};
		ENV->funcall(ENV, ENV->intern(ENV, "throw"), 2, args);	
}

#include <stdio.h>
emacs_value decode_sixel(emacs_env *ENV, ptrdiff_t
						 NARGS, emacs_value *ARGS, void *DATA)
{
		assert(NARGS == 1);
		
		SIXELSTATUS status = SIXEL_FALSE;
		sixel_allocator_t *allocator;
		status = sixel_allocator_new(&allocator, NULL, NULL, NULL, NULL);
        if (SIXEL_FAILED(status)) {
				panic(ENV, "Failed to create allocator.");
        }

		int pwidth, pheight, ncolors;
		unsigned char *palette;
		unsigned char *pixels;

		unsigned char *buf;
		ptrdiff_t len;
		if (!ENV->copy_string_contents(ENV, ARGS[0], NULL, &len)) {
				panic(ENV, "Failed to retrieve string length.");
		}
		if ((buf = malloc(len)) == NULL) {
				panic(ENV, "Failed to allocate buffer.");
		}
		if (!ENV->copy_string_contents(ENV, ARGS[0], (char *) buf, &len)) {
				panic(ENV, "Failed to retrieve string.");
		}

		sixel_decode_raw(buf, len, &pixels, &pwidth, &pheight, &palette, &ncolors, allocator);

		ptrdiff_t output_len = 256 + 12 * (pwidth * pheight);
		char *output, *cur;
		if ((output = malloc(output_len)) == NULL) {
				panic(ENV, "Failed to allocate buffer.");
		}

		cur = output;
		cur += sprintf(cur, "P3\n%d %d\n255\n", pwidth, pheight);
		for (int i = 0; i < pheight * pwidth; i++) {
				cur += sprintf(cur, "%d %d %d\n",
							   *(palette + pixels[i] * 3 + 0),
							   *(palette + pixels[i] * 3 + 1),
							   *(palette + pixels[i] * 3 + 2));
		}

		emacs_value ret = ENV->make_string(ENV, (char *) output, strlen(output));

		free(buf);
		free(output);
		sixel_allocator_unref(allocator);
		return ret;

}

int emacs_module_init(struct emacs_runtime *rt)
{
		// Validate that we're built for this version of Emacs.
		if (rt->size < sizeof (*rt))
				return 1;
		emacs_env *env = rt->get_environment(rt);
		if (env->size < sizeof (*env))
				return 2;

		emacs_value func = env->make_function(env, 1, 1, decode_sixel, NULL, NULL);
		emacs_value symbol = env->intern(env, "sixel-decode-string");
		emacs_value args[] = {symbol, func};
		env->funcall(env, env->intern (env, "defalias"), 2, args);

		return 0;
}
