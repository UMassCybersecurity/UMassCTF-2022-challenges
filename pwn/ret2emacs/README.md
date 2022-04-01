# ret2emacs

So, I've got a reputation at work for doing just about everything in Emacs.
Reading my email, browsing my RSS feeds, running shell commands.. you name it.
Who can blame me? It's more extensible than any other piece of software that
could do those things.

To make a point, I wrote a dynamic module for parsing SIXEL during my lunch
break, and I set up a Rudel server to show it off. I think this is going to blow
the minds of all these VSCode losers.

# Flag

`UMASS{n0T_4_DUnk_0n_3M4c2_By_4nY_M34n2.._n3Xt_Y34r_will_b3_n30V1M}`

# Notes

The `stage0` Dockerfile can't be built unless ASLR is disabled.

```sh
echo 0 > /proc/sys/kernel/randomize_va_space
```

`stage1` is a [load balancer](https://github.com/johnsonjh/ynetd) that spins up
an instance of the `stage0` container for every inbound connection. Only
`stage0` is meant to be exploitable.

`stage1` does require either being run as `privileged` or having access to the
host's Docker socket. I.e.,

```sh
docker run -v /var/run/docker.sock:/var/run/docker.sock -p 6522:6522 jlk/emacs-lb:0.1.0
```
