// Copyright © 2021  Jakob L. Kreuze <zerodaysfordays@sdf.org>

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext('2d');

// ---
const socket = new WebSocket('ws://localhost:8765');
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
                console.log(padded);
                promiseTracker.inFlight[id] = [resolve, reject, padded];
                if (promiseTracker.enabled) {
                    socket.send(JSON.stringify(padded));
                }
            })
        }
    }
}

socket.addEventListener('open', function (event) {
    promiseTracker.enabled = true;
    for (let key of Object.keys(promiseTracker.inFlight)) {
        socket.send(JSON.stringify(promiseTracker.inFlight[key][2]));
    }
});
socket.addEventListener('message', function (event) {
    const response = JSON.parse(event.data);
    const messageId = response.id;
    // resolve
    promiseTracker.inFlight[messageId][0](response.data);
    delete promiseTracker.inFlight[messageId];
});

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
                    if (response === null) {
                        // TODO: Give information on the failure.
                        alert("Failed to register account.")
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
                    });
                    if (response === null) {
                        // TODO: Give information on the failure.
                        alert("Failed to login.")
                        return;
                    }
                    menuState.currentSession = response;
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
                    menuState.currentSession.character = response;
                    menuState.currentMenuName = "main";
                    menuState.updateLabel("character_info", "Current character: " + response.name);
                    menuState.enableId("character_info");
                    renderMenu();

                    // Load in the world from the server.
                    window.localStorage.setItem('world', JSON.stringify(response.world));
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
    load_image("floor.grass.grass_0_old"),
    load_image("floor.grass.grass_1_old"),
    load_image("floor.grass.grass_2_old"),
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
            ctx.fillText("  " + entity.label, x, y);
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
    if (messageBuffer.length >= 4) {
        messageBuffer.shift();
    }
}

// In tiles.
const viewportWidth = 24;
const viewportHeight = 18;

const GAME_STATE = {
    "cameraX": 0,
    "cameraY": 0,
    "tileMap": null,
    // ---
    // TODO: We're clearly missing the portals.
    "loadWorld": function (name) {
        const object = JSON.parse(atob(JSON.parse(window.localStorage.getItem('world')).blob));
        this.tileMap = object["tilemaps"][name];
    }
}

function renderViewport() {
    const worldWidth = GAME_STATE.tileMap[0].length;
    const worldHeight = GAME_STATE.tileMap.length;
    const tileMap = GAME_STATE.tileMap;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '24px monospace';
    for (let y = 0; y < viewportHeight; y++) {
        for (let x = 0; x < viewportWidth; x++) {
            let worldX = x + GAME_STATE["cameraX"];
            let worldY = y + GAME_STATE["cameraY"];
            if (worldY >= 0 && worldY < worldHeight && worldX >= 0 && worldX < worldWidth) {
                let tile_id = tileMap[worldY][worldX];
                ctx.drawImage(TILES[tile_id], x * tileWidth, y * tileHeight);
            }
            // 
        }
    }
    ctx.fillText(
        '🥷',
        (viewportWidth / 2 - 1) * tileWidth + 4,
        (viewportHeight / 2 - 1) * tileHeight + 24
    );
    ctx.font = '16px monospace';
    for (let y = 1; y < 1 + messageBuffer.length; y++) {
        ctx.fillText(messageBuffer[y - 1], 0, viewportHeight * tileHeight + 16 * y);
    }
}

function handleKeyDownGame(e) {
    if (e.key == "8") {
        cameraY--;
    } else if (e.key == "2") {
        cameraY++;
    } else if (e.key == "4") {
        cameraX--;
    } else if (e.key == "6") {
        cameraX++;
    }
    renderViewport();
}
