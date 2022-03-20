# scarymaze2

Assuming you've reverse-engineered the packet obfuscation, this should be a
relatively easy programming challenge. All you need to do is:

- Move your bot to the Maze portal.
- Read off the maze and turn it into a graph.
- Perform your favorite graph search algorithm.
- Translate that into `move_or_interact` packets.

Eventually, there won't be a portal to another maze, it will be a special entity
that, when interacted with, reads the flag out to the user.

# easteregg

Another flag where reverse-engineering the packet obfuscation is the most
difficult part. If you're rigorous with your exploration of the packet format,
you'll see some messages with a type of `sign_text`. If you craft one
arbitrarily with the magic index of `7`, you'll get the flag.

You'd get `7` by enumerating the possible indices, starting at `0`, and noticing
that something following the flag format is visible in the output for sign `7`.

# easterisland

Character data is stored server-side, but maps are stored in `localstorage`.
They're "signed" to prevent tampering, but this is vulnerable to the classic
[length extension
attack](https://en.wikipedia.org/wiki/Length_extension_attack). Every "world" is
a base64-encoded JSON blob, and all worlds in the game are concatenated together
with some arbitrary separator... and the final result is urlencoded. And if the
loader comes across a world it's already seen before, it will overwrite it in
the parsed world. This enables an attacker to modify the world data.

If you read off the tilemap for `grasslands`, the first map`, you'll notice an
island with no obvious way of getting to it. The flag is sent via `message` if
you enter the boundary of the island. My solution was to use the map
modification vulnerability to build a land-bridge to the island.

# adminpanel

Incredibly simple blind SQL injection in the 'Register User' prompt. The nuance
that raises the skill floor slightly is that the password hash is actually
stored as binary data, so you'll need to be somewhat familiar with the functions
available in SQLite for reading them out.

The password for 'administrator' is in the [RockYou
list](https://github.com/zacheller/rockyou), so cracking should be trivial, even
on a modest computer.

# ascension

This is really just botting the entire game. It's easier if you've discovered
the length-extension vulnerability, since you're able to spawn several weak
monsters with incredibly high experience or, even better, spawn the final boss
with the stats of a beginning monster, but it shouldn't be difficult to do
purely though botting. The latter solution only requires that one has
reverse-engineered the packet obfuscation.
