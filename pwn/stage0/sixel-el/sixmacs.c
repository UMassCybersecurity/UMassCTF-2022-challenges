#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include <emacs-module.h>
#include <sixel.h>

#include "md5.c"

// ---

typedef struct emacs_value_tag *emacs_value;
struct emacs_value_tag { void *v; };

// ---

struct hash {
		uint32_t h0, h1, h2, h3;
};

#define CACHESZ 8
static struct hash cache_identifiers[CACHESZ];
static struct emacs_value_tag *cache[CACHESZ];
static int inuse[CACHESZ];

// ---

int plugin_is_GPL_compatible;

void panic(emacs_env *ENV, char *message)
{
		emacs_value message_object = ENV->make_string(ENV, message, strlen(message));
		emacs_value symbol = ENV->intern(ENV, "sixel-decode-string");
		emacs_value args[] = {symbol, message_object};
		ENV->funcall(ENV, ENV->intern(ENV, "throw"), 2, args);
}

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

		md5(buf, len);
		for (int i = 0; i < CACHESZ; i++) {
				if (cache_identifiers[i].h0 == h0 && cache_identifiers[i].h1 == h1 && cache_identifiers[i].h2 == h2 && cache_identifiers[i].h3 == h3) {
						printf("\nFound cached entry: %p\n", *((void **)cache[i]));
						return cache[i];
				}
		}

		sixel_decode_raw(buf, len, &pixels, &pwidth, &pheight, &palette, &ncolors, allocator);

		printf("Alloc: %p\n", pixels);
		printf("Hexdump:\n");
		for (int i = 0; i < pwidth * pheight; i++) {
				printf("%.2x", pixels[i]);
		}
		printf("\n");

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
		// sixel_allocator_free(allocator, pixels);

		emacs_value ret = ENV->make_string(ENV, (char *) output, strlen(output));

		int sentinel = 0;
		for (int i = 0; i < CACHESZ; i++) {
				if (!inuse[i]) {
						sentinel = 1;
						cache_identifiers[i].h0 = h0;
						cache_identifiers[i].h1 = h1;
						cache_identifiers[i].h2 = h2;
						cache_identifiers[i].h3 = h3;
						printf("sizeof: %ld\n", sizeof(struct emacs_value_tag));
						cache[i] = malloc(sizeof(struct emacs_value_tag));
						cache[i]->v = *((void **)ret);
						inuse[i] = 1;
						break;
				}
		}
		if (!sentinel) {
				// Evict the whole cache, except for `i`.
				for (int i = 0; i < CACHESZ; i++) {
						/* cache_identifiers[j].h0 = 0; */
						/* cache_identifiers[j].h1 = 0; */
						/* cache_identifiers[j].h2 = 0; */
						/* cache_identifiers[j].h3 = 0; */
						free(cache[i]);
						inuse[i] = 0;
				}
				cache_identifiers[0].h0 = h0;
				cache_identifiers[0].h1 = h1;
				cache_identifiers[0].h2 = h2;
				cache_identifiers[0].h3 = h3;
				cache[0] = malloc(sizeof(struct emacs_value_tag));
				cache[0]->v = *((void **)ret);
				inuse[0] = 1;
		}

		for (int i = 0; i < CACHESZ; i++) {
				printf("%.2d: [%c] %p\n", i, inuse[i] ? 'x' : ' ', cache[i]);
		}
		printf("\n");

		free(buf);
		free(output);
		sixel_allocator_free(allocator, palette);
		// sixel_allocator_free(allocator, pixels);
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

		memset(cache_identifiers, '\0', sizeof(cache_identifiers));
		memset(cache, '\0', sizeof(cache));
		memset(inuse, '\0', sizeof(inuse));

		emacs_value func = env->make_function(env, 1, 1, decode_sixel, NULL, NULL);
		emacs_value symbol = env->intern(env, "sixel-decode-string");
		emacs_value args[] = {symbol, func};
		env->funcall(env, env->intern (env, "defalias"), 2, args);

		// sizeof(struct emacs_value_tag) = 8

		return 0;
}
