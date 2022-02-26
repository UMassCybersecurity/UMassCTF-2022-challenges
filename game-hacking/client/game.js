// Copyright © 2021  Jakob L. Kreuze <zerodaysfordays@sdf.org>

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext('2d');

// ---

/*
Copyright (c) 2011, Daniel Guerrero
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL DANIEL GUERRERO BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 * Uses the new array typed in javascript to binary base64 encode/decode
 * at the moment just decodes a binary base64 encoded
 * into either an ArrayBuffer (decodeArrayBuffer)
 * or into an Uint8Array (decode)
 *
 * References:
 * https://developer.mozilla.org/en/JavaScript_typed_arrays/ArrayBuffer
 * https://developer.mozilla.org/en/JavaScript_typed_arrays/Uint8Array
 */

/*
MIT License
Copyright (c) 2020 Egor Nepomnyaschih
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/*
// This constant can also be computed with the following algorithm:
const base64abc = [],
    A = "A".charCodeAt(0),
    a = "a".charCodeAt(0),
    n = "0".charCodeAt(0);
for (let i = 0; i < 26; ++i) {
    base64abc.push(String.fromCharCode(A + i));
}
for (let i = 0; i < 26; ++i) {
    base64abc.push(String.fromCharCode(a + i));
}
for (let i = 0; i < 10; ++i) {
    base64abc.push(String.fromCharCode(n + i));
}
base64abc.push("+");
base64abc.push("/");
*/
const base64abc = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"
];

/*
// This constant can also be computed with the following algorithm:
const l = 256, base64codes = new Uint8Array(l);
for (let i = 0; i < l; ++i) {
    base64codes[i] = 255; // invalid character
}
base64abc.forEach((char, index) => {
    base64codes[char.charCodeAt(0)] = index;
});
base64codes["=".charCodeAt(0)] = 0; // ignored anyway, so we just need to prevent an error
*/
const base64codes = [
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 62, 255, 255, 255, 63,
    52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 255, 255, 255, 0, 255, 255,
    255, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 255, 255, 255, 255, 255,
    255, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51
];

function getBase64Code(charCode) {
    if (charCode >= base64codes.length) {
        throw new Error("Unable to parse base64 string.");
    }
    const code = base64codes[charCode];
    if (code === 255) {
        throw new Error("Unable to parse base64 string.");
    }
    return code;
}

function bytesToBase64(bytes) {
    let result = '', i, l = bytes.length;
    for (i = 2; i < l; i += 3) {
        result += base64abc[bytes[i - 2] >> 2];
        result += base64abc[((bytes[i - 2] & 0x03) << 4) | (bytes[i - 1] >> 4)];
        result += base64abc[((bytes[i - 1] & 0x0F) << 2) | (bytes[i] >> 6)];
        result += base64abc[bytes[i] & 0x3F];
    }
    if (i === l + 1) { // 1 octet yet to write
        result += base64abc[bytes[i - 2] >> 2];
        result += base64abc[(bytes[i - 2] & 0x03) << 4];
        result += "==";
    }
    if (i === l) { // 2 octets yet to write
        result += base64abc[bytes[i - 2] >> 2];
        result += base64abc[((bytes[i - 2] & 0x03) << 4) | (bytes[i - 1] >> 4)];
        result += base64abc[(bytes[i - 1] & 0x0F) << 2];
        result += "=";
    }
    return result;
}

function base64ToBytes(str) {
    if (str.length % 4 !== 0) {
        throw new Error("Unable to parse base64 string.");
    }
    const index = str.indexOf("=");
    if (index !== -1 && index < str.length - 2) {
        throw new Error("Unable to parse base64 string.");
    }
    let missingOctets = str.endsWith("==") ? 2 : str.endsWith("=") ? 1 : 0,
        n = str.length,
        result = new Uint8Array(3 * (n / 4)),
        buffer;
    for (let i = 0, j = 0; i < n; i += 4, j += 3) {
        buffer =
            getBase64Code(str.charCodeAt(i)) << 18 |
            getBase64Code(str.charCodeAt(i + 1)) << 12 |
            getBase64Code(str.charCodeAt(i + 2)) << 6 |
            getBase64Code(str.charCodeAt(i + 3));
        result[j] = buffer >> 16;
        result[j + 1] = (buffer >> 8) & 0xFF;
        result[j + 2] = buffer & 0xFF;
    }
    return result.subarray(0, result.length - missingOctets);
}

// ---
var TOKEN = null;
var socket = new WebSocket('ws://localhost:8765');

const SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
];

function serialize(data) {
    let encoder = new TextEncoder();
    let encoded = encoder.encode(JSON.stringify(data));
    let choice = Math.floor(Math.random() * SBOX.length);
    let nonce = SBOX[choice];
    let key = nonce;
    for (let i = 0; i < encoded.length; i++) {
        encoded[i] ^= key;
        key = SBOX[key];
    }
    let decoder = new TextDecoder();
    let packet = new Uint8Array(encoded.length + 1);
    packet[0] = nonce;
    for (let i = 0; i < encoded.length; i++) {
        packet[i+1] = encoded[i];
    }
    return bytesToBase64(packet);
}

function deserialize(chunk){
    chunk = base64ToBytes(chunk);
    let nonce = chunk[0];
    let key = nonce;
    chunk = chunk.slice(1);
    for (let i = 0; i < chunk.length; i++) {
        chunk[i] ^= key;
        key = SBOX[key];
    }
    let decoder = new TextDecoder();
    return JSON.parse(decoder.decode(chunk));
}

function initializeSocket(socket, reconnect) {
    socket.addEventListener('open', function (event) {
        if (reconnect && TOKEN !== null) {
            socket.send(serialize({ "type": "reconnect", "token": TOKEN }));
        }
        promiseTracker.enabled = true;
        for (let key of Object.keys(promiseTracker.inFlight)) {
            socket.send(serialize(promiseTracker.inFlight[key][2]));
        }
    });
    socket.addEventListener('message', function (event) {
        if (event.data === {}) {
            return;
        }
        const response = deserialize(event.data);
        if (response.hasOwnProperty("id")) {
            const messageId = response.id;
            promiseTracker.inFlight[messageId][0](response.data);
            delete promiseTracker.inFlight[messageId];
        } else if (response.hasOwnProperty("error")) {
            alert(response.error);
        } else {
            alert("Unhandled server-side exception.");
        }
    });
    socket.addEventListener('close', function (event) {
        alert("Received disconnect from server. Reconnecting in 1s.");
        setTimeout(function() {
            alert("Attempting to reconnect...");
            socket = new WebSocket('ws://localhost:8765');
            initializeSocket(socket, true);
        }, 1000);
    });
}

initializeSocket(socket, false);
const promiseTracker = {
    "enabled": false,
    "inFlight": {},
};

function queuePacket(data) {
    for (let i = 0;; i++) {
        const id = (i).toString();
        if (!promiseTracker.inFlight.hasOwnProperty(id)) {
            return new Promise((resolve, reject) => {
                const padded = {
                    "id": id,
                    "data": data
                };
                promiseTracker.inFlight[id] = [resolve, reject, padded];
                if (promiseTracker.enabled) {
                    socket.send(serialize(padded));
                }
            })
        }
    }
}

// ---

const MENU_STATE = {
    "currentSession": null,
    "currentItem": 0,
    "currentMenuName": "main",
    "menus": {
        "main": [
            {
                "type": "button",
                "id": "register",
                "label": "Register Account",
                "enabled": true,
                "action": (menuState) => {
                    menuState.currentMenuName = "register";
                }
            },
            {
                "type": "button",
                "id": "login",
                "label": "Login",
                "enabled": true,
                "action": (menuState) => {
                    menuState.currentMenuName = "login";
                }
            },
            {
                "type": "label",
                "id": "account_info",
                "label": "Logged in as: ",
                "enabled": false,
            },
            {
                "type": "label",
                "id": "character_info",
                "label": "Playing as: ",
                "enabled": false,
            },
            {
                "type": "spacer",
                "id": "spacer",
                "height": 16,
                "enabled": false,
            },
            {
                "type": "button",
                "id": "start",
                "label": "Start Game",
                "enabled": false,
                "action": (menuState) => {
                    GAME_STATE.loadWorld("grasslands");
                    window.removeEventListener('load', renderMenu);
                    document.removeEventListener('keydown', handleKeyDownMenu);
                    window.addEventListener('load', renderViewport);
                    document.addEventListener('keydown', handleKeyDownGame);
                    canvas.addEventListener('click', handleMouseClickGame);
                    renderViewport();
                }
            },
            {
                "type": "button",
                "id": "create_character",
                "label": "Create New Character",
                "enabled": false,
                "action": (menuState) => {
                    menuState.currentMenuName = "new_character";
                }
            },
            {
                "type": "button",
                "id": "logout",
                "label": "Log Out",
                "enabled": false,
            }
        ],
        "register": [
            {
                "type": "entry",
                "id": "username",
                "label": "Username",
                "enabled": true,
                "content": ""
            },
            {
                "type": "password",
                "id": "password1",
                "label": "Password",
                "enabled": true,
                "content": ""
            },
            {
                "type": "password",
                "id": "password2",
                "label": "Confirm Password",
                "enabled": true,
                "content": ""
            },
            {
                "type": "spacer",
                "height": 32,
                "enabled": true,
            },
            {
                "type": "button",
                "id": "submit",
                "label": "Submit",
                "enabled": true,
                "action": async function (menuState) {
                    if (menuState.getInput("password1") != menuState.getInput("password2")) {
                        alert("Passwords do not match.");
                        return;
                    }
                    const response = await queuePacket({
                        "type": "register",
                        "username": menuState.getInput("username"),
                        "password": menuState.getInput("password1"),
                    });
                    if (response.hasOwnProperty("error")) {
                        // TODO: Give information on the failure.
                        alert(`Failed to register account: ${response.error}`);
                        return;
                    }
                    menuState.currentSession = response;
                    menuState.currentMenuName = "main";
                    menuState.disableId("register");
                    menuState.disableId("login");
                    menuState.updateLabel("account_info", "Logged in as: " + response.username);
                    menuState.enableId("account_info");
                    menuState.enableId("spacer");
                    menuState.enableId("start");
                    menuState.enableId("create_character");
                    menuState.enableId("logout");
                    menuState.currentItem = 0;
                    renderMenu();
                }
            }
        ],
        "login": [
            {
                "type": "entry",
                "id": "username",
                "label": "Username",
                "enabled": true,
                "content": ""
            },
            {
                "type": "password",
                "id": "password",
                "label": "Password",
                "enabled": true,
                "content": ""
            },
            {
                "type": "spacer",
                "height": 32,
                "enabled": true
            },
            {
                "type": "button",
                "id": "submit",
                "label": "Submit",
                "enabled": true,
                "action": async function (menuState) {
                    const response = await queuePacket({
                        "type": "login",
                        "username": menuState.getInput("username"),
                        "password": menuState.getInput("password"),
                        "world": window.localStorage.getItem('world'),
                    });
                    if (response.hasOwnProperty("error")) {
                        alert(`Failed to login: ${response.error}`);
                        return;
                    }
                    if (response.hasOwnProperty("flag")) {
                        alert(`Congratulations! ${response.flag}`);
                        return;
                    }
                    menuState.currentSession = response;
                    GAME_STATE.character = response.character;
                    menuState.currentMenuName = "main";
                    menuState.disableId("register");
                    menuState.disableId("login");
                    menuState.updateLabel("account_info", "Logged in as: " + response.username);
                    menuState.enableId("account_info");
                    if (response.character !== null) {
                        menuState.updateLabel("character_info", "Current character: " + response.character.name);
                        menuState.enableId("character_info");
                    }
                    menuState.enableId("spacer");
                    menuState.enableId("start");
                    menuState.enableId("create_character");
                    menuState.enableId("logout");
                    menuState.currentItem = 0;
                    renderMenu();

                    // Save our token.
                    TOKEN = response.token;
                }

            }
        ],
        "new_character": [
            {
                "type": "entry",
                "id": "name",
                "label": "Player Name",
                "enabled": true,
                "content": ""
            },
            {
                "type": "numerical_range",
                "id": "age",
                "label": "Age",
                "enabled": true,
                "value": 18,
                "minimum": 18,
                "maximum": 99
            },
            {
                "type": "choice",
                "id": "class",
                "label": "Class",
                "enabled": true,
                "index": 0,
                "choices": [
                    "🧚 fairy",
                    "👩‍⚕️ medic",
                    "👨‍🏭 pyro",
                    "🥷 ninja",
                    "🧙 subway panhandler",
                    "🤡 clown",
                    "👽 alien",
                    "🦝 raccoon",
                    "🦖 t-rex",
                    "👨‍🌾 farmer",
                    "👯 dynamic duo",
                    "🏋️ tank",
                    "🧜 fish",
                    "🤠 post malone"
                ]
            },
            {
                "type": "choice",
                "id": "order",
                "label": "Law vs. Chaos",
                "enabled": true,
                "index": 0,
                "choices": [
                    "lawful",
                    "neutral",
                    "chaotic"
                ]
            },
            {
                "type": "choice",
                "id": "morality",
                "label": "Good vs. Evil",
                "enabled": true,
                "index": 0,
                "choices": [
                    "good",
                    "neutral",
                    "evil"
                ]
            },
            {
                "type": "choice",
                "id": "bonus",
                "label": "Bonus Item",
                "enabled": true,
                "index": 0,
                "choices": [
                    "🌂 umbrella (weapon)",
                    "👝 purse (weapon)",
                    "🩹 band-aid (item; consumable)",
                    "🎸 guitar (item)",
                    "💋 aphrodisiac (item; consumable)",
                ]
            },
            {
                "type": "spacer",
                "height": 32
            },
            {
                "type": "button",
                "id": "submit",
                "label": "Submit",
                "enabled": true,
                "action": async function (menuState) {
                    if (menuState.currentSession && menuState.currentSession.character !== null &&
                        !window.confirm("This will delete your current character. Are you sure?")) {
                        return;
                    }
                    const response = await queuePacket({
                        "type"     : "create_character",
                        "name"     : menuState.getInput("name"),
                        "age"      : menuState.getInput("age"),
                        "class"    : menuState.getInput("class"),
                        "order"    : menuState.getInput("order"),
                        "morality" : menuState.getInput("morality"),
                        "bonus"    : menuState.getInput("bonus"),
                    });
                    if (response === null) {
                        alert("Failed to create character.")
                        return;
                    }
                    menuState.currentSession.character = response.character;
                    GAME_STATE.character = response.character;
                    menuState.currentMenuName = "main";
                    menuState.updateLabel("character_info", "Current character: " + response.character.name);
                    menuState.enableId("character_info");
                    menuState.enableId("start");
                    renderMenu();

                    // Load in the world from the server.
                    window.localStorage.setItem('world', JSON.stringify(response.world));

                    // Save our token.
                    TOKEN = response.token;
                }

            }
        ]
    },
    // ---
    "currentMenu": function () {
        return this.menus[this.currentMenuName];
    },
    "getInput": function (id) {
        const menu = this.currentMenu();
        for (let entity of menu) {
            if ((entity.type == "entry" || entity.type == "password") && entity.id == id) {
                return entity.content;
            } else if (entity.type == "numerical_range" && entity.id == id) {
                return entity.value;
            } else if (entity.type == "choice" && entity.id == id) {
                return entity.choices[entity.index];
            }
        }
    },
    "updateLabel": function (id, newLabel) {
        const menu = this.currentMenu();
        for (let entity of menu) {
            if (entity.type == "label" && entity.id == id) {
                entity.label = newLabel;
            }
        }
    },
    "disableId": function (id) {
        const menu = this.currentMenu();
        for (let entity of menu) {
            if (entity.id == id) {
                entity.enabled = false;
            }
        }
    },
    "enableId": function (id) {
        const menu = this.currentMenu();
        for (let entity of menu) {
            if (entity.id == id) {
                entity.enabled = true;
            }
        }
    }
}


// ---

function load_image(name) {
    let img = new Image();
    img.src = 'assets/' + name.replace(/\./g, '/') + '.png';
    return img;
}

const tileWidth = 32;
const tileHeight = 32;
const TILES = [
    load_image("floor.cobble_blood_10_new"),
    load_image("water.deep_water"),
    load_image("floor.grass.grass_0_old"),
    load_image("floor.grass.grass_1_old"),
    load_image("floor.grass.grass_2_old"),
    load_image("floor.grass.grass0-dirt-mix_3"),
    load_image("wall.brick_brown_0"),
    load_image("floor.rect_gray_1_old"),
    load_image("floor.sand_1"),
    load_image("floor.sand_2"),
    load_image("floor.sand_3"),
    load_image("floor.sand_4"),
    load_image("floor.sandstone_floor_1"),
    load_image("wall.sandstone_wall_0"),
    load_image("floor.ice_0_old"),
    load_image("floor.ice_1_old"),
    load_image("floor.ice_2_old"),
    load_image("floor.ice_3_old"),
    load_image("wall.cobalt_stone_1"),
    load_image("floor.black_cobalt_1")
];

const TITLE_COLOR = ["#ff3b00", "#ff5c00", "#ff8400", "#ffa500", "#ffbf00", "#ffe000", "#ffed00"];
const MAPLE = ["::::    ::::      :::     :::::::::  :::        ::::::::::",
               "+:+:+: :+:+:+   :+: :+:   :+:    :+: :+:        :+:       ",
               "+:+ +:+:+ +:+  +:+   +:+  +:+    +:+ +:+        +:+       ",
               "+#+  +:+  +#+ +#++:++#++: +#++:++#+  +#+        +#++:++#  ",
               "+#+       +#+ +#+     +#+ +#+        +#+        +#+       ",
               "#+#       #+# #+#     #+# #+#        #+#        #+#       ",
               "###       ### ###     ### ###        ########## ##########"];
const QUEST = ["  ::::::::   :::    ::: ::::::::::  ::::::::  ::::::::::: ",
               " :+:    :+:  :+:    :+: :+:        :+:    :+:     :+:     ",
               " +:+    +:+  +:+    +:+ +:+        +:+            +:+     ",
               " +#+    +:+  +#+    +:+ +#++:++#   +#++:++#++     +#+     ",
               " +#+  # +#+  +#+    +#+ +#+               +#+     +#+     ",
               " #+#   +#+   #+#    #+# #+#        #+#    #+#     #+#     ",
               "  ###### ###  ########  ##########  ########      ###     "];;

function renderMenu() {
    ctx.fillStyle = "#333333";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < canvas.height / tileHeight; y++) {
        for (let x = 0; x < canvas.width / tileWidth; x++) {
            ctx.drawImage(TILES[0], x * tileWidth, y * tileHeight);
        }
    }

    ctx.font = 'bold 10px monospace';
    let initialWidth = ctx.measureText(MAPLE[0]).width;
    for (let y = 0; y < MAPLE.length; y++) {
        const x = (canvas.width - initialWidth) / 2;
        ctx.fillStyle = TITLE_COLOR[y];
        ctx.fillText(MAPLE[y], x, 32 + (y + 1) * 8);
    }
    initialWidth = ctx.measureText(QUEST[0]).width;
    for (let y = 0; y < QUEST.length; y++) {
        const x = (canvas.width - initialWidth) / 2;
        ctx.fillStyle = TITLE_COLOR[y];
        ctx.fillText(QUEST[y], x, 32 + 64 + (y + 1) * 8);
    }

    ctx.fillStyle = "white";
    ctx.font = 'bold 16px monospace';
    const currentMenu = MENU_STATE.currentMenu();
    let i = 0;
    let x = 256;
    let y = 256;
    let prefix;
    for (let entity of currentMenu) {
        if (!entity.enabled) {
            continue;
        }
        switch (entity.type) {
        case "button":
            prefix = i == MENU_STATE.currentItem ? "> " : "  ";
            ctx.fillText(prefix + entity.label, x, y);
            y += 16;
            break;
        case "entry":
            prefix = i == MENU_STATE.currentItem ? "> " : "  ";
            ctx.fillText(prefix + entity.label + ": " + entity.content, x, y);
            y += 16;
            break;
        case "password":
            const text = Array.from(entity.content).map((_) => "*").join("")
            prefix = i == MENU_STATE.currentItem ? "> " : "  ";
            ctx.fillText(prefix + entity.label + ": " + text, x, y);
            y += 16;
            break;
        case "numerical_range":
            prefix = i == MENU_STATE.currentItem ? "> " : "  ";
            ctx.fillText(prefix + entity.label + ": " + entity.value, x, y);
            y += 16;
            break;
        case "choice":
            prefix = i == MENU_STATE.currentItem ? "> " : "  ";
            ctx.fillText(prefix + entity.label + ": " + entity.choices[entity.index], x, y);
            y += 16;
            break;
        case "label":
            prefix = i == MENU_STATE.currentItem ? "> " : "  ";
            ctx.fillText(prefix + entity.label, x, y);
            y += 16;
            break;
        case "spacer":
            y += entity.height;
            break;
        }
        i++;
    }
}

function handleKeyDownMenu(e) {
    const entities = MENU_STATE.currentMenu().filter((ent) => ent.enabled);
    const entity = entities[MENU_STATE.currentItem];
    switch (e.key) {
    case "ArrowUp":
        if (MENU_STATE.currentItem > 0) {
            MENU_STATE.currentItem--;
        }
        break;
    case "ArrowDown":
        const upperBound = MENU_STATE.currentMenu().filter((ent) => ent.enabled).length;
        if (MENU_STATE.currentItem < upperBound - 1) {
            MENU_STATE.currentItem++;
        }
        break;
    case "ArrowRight":
        if (entity.type == "numerical_range" && entity.value < entity.maximum) {
            entity.value++;
        } else if (entity.type == "choice" && entity.index < entity.choices.length - 1) {
            entity.index++;
        }
        break;
    case "ArrowLeft":
        if (entity.type == "numerical_range" && entity.value > entity.minimum) {
            entity.value--;
        } else if (entity.type == "choice" && entity.index > 0) {
            entity.index--;
        }
        break;
    case "Enter":
        if (entity.type == "button") {
            entity.action(MENU_STATE);
        }
        MENU_STATE.currentItem = 0;
        break;
    case "Backspace":
        if (entity.type == "entry" || entity.type == "password") {
            entity.content = entity.content.substring(0, entity.content.length - 1);
        } else {
            // TODO: We might need to track a trail so we can go back to the
            // previous menu... in the case that the previous menu isn't
            // guaranteed to be main.
            MENU_STATE.currentMenuName = "main";
            MENU_STATE.currentItem = 0;
        }
        break;
    default:
        if ((entity.type == "entry" || entity.type == "password") && e.key.length == 1) {
            entity.content += e.key;
        }
        break;
    }
    renderMenu();
}

window.addEventListener('load', renderMenu);
document.addEventListener('keydown', handleKeyDownMenu);

// ---

// Message buffer

const messageBuffer = [];
function log(message) {
    messageBuffer.push(message);
    if (messageBuffer.length >= 8) {
        messageBuffer.shift();
    }
}

// In tiles.
const viewportWidth = 24;
const viewportHeight = 18;

const alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '/', '='];
function splitBase64Chunks(blob) {
    let chunks = [];
    let unchanged;

    while (blob.length > 0) {
        unchanged = blob.length;
        for (let i = 0; i < blob.length; i++) {
            if (!alphabet.includes(String.fromCharCode(blob[i]))) {
                chunks.push(blob.slice(0, i))
                while (i < blob.length && !alphabet.includes(String.fromCharCode(blob[i])))
                    i++;
                blob.splice(0, i);
                break;
            }
        }
        if (blob.length == unchanged) {
            chunks.push(blob);
            break;
        }
    }
    return chunks;
}

// https://stackoverflow.com/questions/57873879/buffers-and-url-encoding-in-node-js
const isUrlSafe = (char) => {
  return /[a-zA-Z0-9\-_~.]+/.test(char)
}

// const urlEncodeBytes = (buf) => {
//   let encoded = ''
//   for (let i = 0; i < buf.length; i++) {
//     const charBuf = Uint8Array.from('00', 'hex')
//     charBuf.writeUInt8(buf[i])
//     const char = charBuf.toString()
//     // if the character is safe, then just print it, otherwise encode
//     if (isUrlSafe(char)) {
//       encoded += char
//     } else {
//       encoded += `%${charBuf.toString('hex').toUpperCase()}`
//     }
//   }
//   return encoded
// }

const urlDecodeBytes = (encoded) => {
  let decoded = [];
  for (let i = 0; i < encoded.length; i++) {
      if (encoded[i] === '%') {
          decoded.push(parseInt(encoded.substring(i + 1, i + 3), 16))
          i += 2
      } else {
          decoded.push(encoded.charCodeAt(i));
      }
  }
  return decoded
}

const GAME_STATE = {
    "character": null,
    "mode": "movement",
    "position": {
        "x": 0,
        "y": 0
    },
    "inventory": {
        "selected": 0,
    },
    "tileMap": null,
    "mobs": [],
    // ---
    "loadWorld": function (name) {
        let decoder = new TextDecoder();
        const object = JSON.parse(window.localStorage.getItem('world')).blob;
        const blobs = splitBase64Chunks(urlDecodeBytes(object));
        for (let blob of blobs) {
            let decoded = JSON.parse(atob(decoder.decode(new Uint8Array(blob))));
            if (decoded["location"] !== name) {
                continue;
            }
            this.tileMap = JSON.parse(decoder.decode(fflate.unzlibSync(base64ToBytes(decoded["tilemap"]))));
            this.mobs = [];
            for (let mob of decoded["mobs"]) {
                this.mobs.push({ ...mob});
            }
        }
    }
}

function renderViewport() {
    const worldWidth = GAME_STATE.tileMap[0].length;
    const worldHeight = GAME_STATE.tileMap.length;
    const tileMap = GAME_STATE.tileMap;

    const playerPosition = GAME_STATE.position;
    const cameraX = playerPosition.x - viewportWidth / 2;
    const cameraY = playerPosition.y - viewportHeight / 2;

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = '24px monospace';
    for (let y = 0; y < viewportHeight; y++) {
        for (let x = 0; x < viewportWidth; x++) {
            let worldX = x + cameraX;
            let worldY = y + cameraY;
            if (worldY >= 0 && worldY < worldHeight && worldX >= 0 && worldX < worldWidth) {
                let tile_id = tileMap[worldY][worldX];
                ctx.drawImage(TILES[tile_id + 1], x * tileWidth, y * tileHeight);
            } else {
                // Draw water.
                ctx.drawImage(TILES[1], x * tileWidth, y * tileHeight);
            }
            //
        }
    }
    for (let entity of GAME_STATE.mobs) {
        const viewportX = entity.position.x - cameraX;
        const viewportY = entity.position.y - cameraY;
        if (viewportY >= 0 && viewportY < viewportHeight && viewportX >= 0 && viewportX < viewportWidth) {
            ctx.fillText(
                entity["world_view"],
                viewportX * tileWidth + 4,
                viewportY * tileHeight + 24
            );
        }
    }
    ctx.fillText(
        GAME_STATE.character["class"],
        (viewportWidth / 2) * tileWidth + 4,
        (viewportHeight / 2) * tileHeight + 24
    );
    ctx.font = '16px monospace';
    ctx.fillStyle = "#000000";
    ctx.lineWidth = 4;
    ctx.moveTo(0, viewportHeight * tileHeight);
    ctx.lineTo(canvas.width, viewportHeight * tileHeight);
    ctx.stroke();
    for (let y = 1; y < 1 + messageBuffer.length; y++) {
        ctx.fillText(messageBuffer[y - 1], 4, 2 + viewportHeight * tileHeight + 16 * y);
    }

    let line;
    if (GAME_STATE.mode === "inventory") {

        let rectHeight = 0;
        for (let y = 0; y < GAME_STATE.character.inventory.length; y++) {
            line = GAME_STATE.character.inventory[y]["inventory_view"];
            line = (GAME_STATE.inventory.selected == y ? "> " : "  ") + line;
            rectHeight += 12;
        }
        rectHeight = Math.max(rectHeight, tileHeight * (viewportHeight / 2));

        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, tileWidth * viewportWidth, rectHeight);
        ctx.fillStyle = "#000000";
        for (let y = 1; y < 1 + GAME_STATE.character.inventory.length; y++) {
            line = GAME_STATE.character.inventory[y - 1]["inventory_view"];
            line = (GAME_STATE.inventory.selected == y - 1 ? "> " : "  ") + line;
            line = (GAME_STATE.character.equipped && GAME_STATE.character.equipped.find(item => item.id === GAME_STATE.character.inventory[y - 1].id)) ? line + "(equipped)" : line;
            ctx.fillText(line, 0, tileHeight + 16 * y);
        }


        ctx.fillText(`name: ${GAME_STATE.character["name"]}`, canvas.width - 256, tileHeight + 16 * 0);
        ctx.fillText(`age: ${GAME_STATE.character["age"]}`, canvas.width - 256, tileHeight + 16 * 1);
        ctx.fillText(`hp: ${GAME_STATE.character["health"]}/${GAME_STATE.character["max_health"]}`, canvas.width - 256, tileHeight + 16 * 2);
        ctx.fillText(`lvl: ${GAME_STATE.character["level"]}`, canvas.width - 256, tileHeight + 16 * 3);
        ctx.fillText(`exp: ${GAME_STATE.character["experience"]}`, canvas.width - 256, tileHeight + 16 * 4);
        ctx.fillText(`str: ${GAME_STATE.character["strength"]}`, canvas.width - 256, tileHeight + 16 * 5);
        ctx.fillText(`con: ${GAME_STATE.character["constitution"]}`, canvas.width - 256, tileHeight + 16 * 6);
        ctx.fillText(`dex: ${GAME_STATE.character["initiative"]}`, canvas.width - 256, tileHeight + 16 * 7);
    }
}


async function handleKeyDownMovementMode(e) {
    let response;
    switch (e.key) {
    case "8" :
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "north"
        });
        break;
    case "9" :
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "northeast"
        });
        break;
    case "6":
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "east"
        });
        break;
    case "3":
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "southeast"
        });
        break;
    case "2":
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "south"
        });
        break;
    case "1":
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "southwest"
        });
        break;
    case "4":
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "west"
        });
        break;
    case "7":
        response = await queuePacket({
            "type": "move_or_interact",
            "direction": "northwest"
        });
        break;
    case ".":
        response = await queuePacket({
            "type": "wait",
        });
        break;
    case ",":
        response = await queuePacket({
            "type": "pickup_all",
        });
        break;
    case "i":
        GAME_STATE.mode = "inventory";
        GAME_STATE.inventory.selected = 0;
        break;
    }
    return response;
}

async function handleKeyDownInventoryMode(e) {
    let response;
    switch (e.key) {
    case "2":
        if (GAME_STATE.inventory.selected < GAME_STATE.character.inventory.length - 1) {
            GAME_STATE.inventory.selected++;
        }
        break;
    case "8":
        if (GAME_STATE.inventory.selected > 0) {
            GAME_STATE.inventory.selected--;
        }
        break;
    case "d":
        {
            const idx = GAME_STATE.inventory.selected;
            const item = GAME_STATE.character.inventory[idx];
            GAME_STATE.character.inventory.splice(idx, 1);
            response = await queuePacket({
                "type": "drop_item",
                "id": item.id
            });
            GAME_STATE.mode = "movement";
        }
        break;
    // FIXME: Both cases make assumptions that will probably not hold when the
    // world updates are slightly more complicated.
    case "e":
        {
            const idx = GAME_STATE.inventory.selected;
            const item = GAME_STATE.character.inventory[idx];
            response = await queuePacket({
                "type": "equip_item",
                "id": item.id
            });
            if (response.map((x) => x.hasOwnProperty("text") && (x.text.includes("Too many items equipped") || x.text.includes("You cannot equip a"))).
                reduce((a, b) => a || b, false)) {
                break;
            }
            // GAME_STATE.character.inventory.splice(idx, 1);
            if (GAME_STATE.character.hasOwnProperty("equipped")) {
                GAME_STATE.character.equipped.push(item);
            } else {
                GAME_STATE.character.equipped = [item];
            }
        }
        break;
    case "c":
        {
            const idx = GAME_STATE.inventory.selected;
            const item = GAME_STATE.character.inventory[idx];
            response = await queuePacket({
                "type": "consume_item",
                "id": item.id
            });

            if (response.map((x) => x.hasOwnProperty("text") && x.text.includes("You cannot eat a"))
                .reduce((a, b) => a || b, false)) {
                break;
            }
            GAME_STATE.character.inventory.splice(idx, 1);
        }
        break;
    case "t":
        const idx = GAME_STATE.inventory.selected;
        const item = GAME_STATE.character.inventory[idx];
        response = await queuePacket({
            "type": "throw_item",
            "id": item.id
        });
        GAME_STATE.character.inventory.splice(idx, 1);
    case "Escape":
        GAME_STATE.mode = "movement";
        break;
    }
    return response;
}

async function handleKeyDownGame(e) {
    let response;
    switch(GAME_STATE.mode) {
    case "movement":
        response = await handleKeyDownMovementMode(e);
        break;
    case "inventory":
        response = await handleKeyDownInventoryMode(e);
        break;
    }
    if (response) {
        for (let update of response) {
            console.log(update);
            switch (update.type) {
            case "update_position":
                GAME_STATE.position.x = update.x;
                GAME_STATE.position.y = update.y;
                break;
            case "new_mob":
                // Make sure this isn't a duplicate.
                let sentinel = false;
                for (let mob of GAME_STATE.mobs) {
                    if (mob.id === update.entity.id) {
                        sentinel = true;
                    }
                }
                if (!sentinel) {
                    GAME_STATE.mobs.push(update.entity);
                }
                break;
            case "new_item":
                GAME_STATE.character.inventory.push(update.item);
                break;
            case "become":
                for (let i = 0; i < GAME_STATE.mobs.length; i++) {
                    if (GAME_STATE.mobs[i].id === update.id) {
                        GAME_STATE.mobs[i] = update.replacement;
                    }
                }
                break;
            case "delete_mob":
                for (let i = 0; i < GAME_STATE.mobs.length; i++) {
                    if (GAME_STATE.mobs[i].id === update.id) {
                        GAME_STATE.mobs.splice(i, 1);
                        break;
                    }
                }
                break;
            case "move_mob":
                for (let i = 0; i < GAME_STATE.mobs.length; i++) {
                    if (GAME_STATE.mobs[i].id === update.id) {
                        GAME_STATE.mobs[i].position = update.new_position;
                        break;
                    }
                }
                break;
            case "move_mob_animate":
                for (let i = 0; i < GAME_STATE.mobs.length; i++) {
                    if (GAME_STATE.mobs[i].id === update.id) {
                        GAME_STATE.mobs[i].position = update.new_position;
                        break;
                    }
                }
                await wait(50);
                renderViewport();
                break;
            case "message":
                log(update.text);
                break;
            case "teleport_player":
                GAME_STATE.loadWorld(update.target_world)
                break;
            case "update_world":
                window.localStorage.setItem('world', JSON.stringify(update.world));
                break;
            case "update_player":
                GAME_STATE.character = update.entity;
                break;
            case "game_over":
                window.localStorage.setItem('world', null);
                GAME_STATE["character"] = null;
                GAME_STATE["mode"] = "movement";
                GAME_STATE["position"] = { "x": 0, "y": 0 };
                GAME_STATE["inventory"] = { "selected": 0 };
                GAME_STATE["tileMap"] = null;
                GAME_STATE["mobs"] = [];
                GAME_OVER_MESSAGE = update.text;
                window.removeEventListener('load', renderViewport);
                document.removeEventListener('keydown', handleKeyDownGame);
                document.removeEventListener('click', handleMouseClickGame);
                document.addEventListener('keydown', handleKeyDownGameOver);
                MENU_STATE.disableId("character_info");
                MENU_STATE.disableId("start");
                renderGameOver();
                return;
            }
        }
    }
    renderViewport();
}

async function handleKeyDownGameOver(e) {
    renderMenu();
    document.removeEventListener('keydown', handleKeyDownGameOver);
    window.addEventListener('load', renderMenu);
    document.addEventListener('keydown', handleKeyDownMenu);
}

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const canvasLeft = canvas.offsetLeft + canvas.clientLeft;
const canvasTop = canvas.offsetTop + canvas.clientTop;
async function handleMouseClickGame(e) {
    const playerPosition = GAME_STATE.position;
    const cameraX = playerPosition.x - viewportWidth / 2;
    const cameraY = playerPosition.y - viewportHeight / 2;
    const x = event.pageX - canvasLeft;
    const y = event.pageY - canvasTop;
    const viewportX = cameraX + Math.floor(x / tileWidth);
    const viewportY = cameraY + Math.floor(y / tileWidth);

    for (let mob of GAME_STATE.mobs) {
        if (mob.position.x == viewportX && mob.position.y == viewportY) {
            switch (mob.type) {
            case "sign":
                const response = await queuePacket({
                    "type": "sign_text",
                    "id": mob.sign_id
                });
                log(`The sign reads: "${response.text}"`);
                break;
            default:
                log(`This is a ${mob.type}.`);
            }
        }
    }
    renderViewport();
}


let GAME_OVER_MESSAGE = "";


function renderGameOver() {
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.fillText("Game over...", 0, 0);
    ctx.fillText(GAME_OVER_MESSAGE, 0, 32);
    ctx.fillText("<Press any key to continue.>", 0, 64);
}

// --- TEMPORARY; DO NOT COMMIT TO VC
async function skipMenu() {
    let response = await queuePacket({
        "type": "register",
        "username": "Jakob",
        "password": "test",
    });
    console.log(response);
    GAME_STATE.character = response.character;
    TOKEN = response.token;
    response = await queuePacket({
        "type"     : "create_character",
        "name"     : "jakob",
        "age"      : 18,
        "class"    : "🤠 post malone",
        "order"    : "lawful",
        "morality" : "evil",
        "bonus"    : "🌂 umbrella (weapon)",
    });
    GAME_STATE.character = response.character;
    window.localStorage.setItem('world', JSON.stringify(response.world));
    TOKEN = response.token;

    GAME_STATE.loadWorld("grasslands");
    window.removeEventListener('load', renderMenu);
    document.removeEventListener('keydown', handleKeyDownMenu);
    window.addEventListener('load', renderViewport);
    document.addEventListener('keydown', handleKeyDownGame);
    canvas.addEventListener('click', handleMouseClickGame);
    renderViewport();
}
skipMenu();
// ---
