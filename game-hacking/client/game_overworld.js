function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min) + min); //The maximum is exclusive and the minimum is inclusive
}


// Load all images.

function load_image(name) {
    let img = new Image();
    img.src = 'assets/' + name.replace(/\./g, '/') + '.png';
    return img;
}

const TILES = [
    load_image("floor.grass.grass_0_old"),
    load_image("floor.grass.grass_1_old"),
    load_image("floor.grass.grass_2_old"),
];

// Message buffer

const messageBuffer = [];
function log(message) {
    messageBuffer.push(message);
    if (messageBuffer.length >= 4) {
        messageBuffer.shift();
    }
}

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext('2d');
// ctx.drawImage(img, 0, 0);
// ctx.fillText('🥷', 0 + 4, 0 + 24);

// ---

const worldWidth = 512;
const worldHeight = 512
const objects = [];

// In tiles.
const viewportWidth = 24;
const viewportHeight = 18;

const tileMap = [];
for (let y = 0; y < worldHeight; y++) {
    tileMap.push([]);
    for (let x = 0; x < worldWidth; x++) {
        tileMap[y].push(getRandomInt(0, 3));
    }
}

const tileWidth = 32;
const tileHeight = 32;

function renderViewport(cameraX, cameraY) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '24px monospace';
    for (let y = 0; y < viewportHeight; y++) {
        for (let x = 0; x < viewportWidth; x++) {
            let worldX = x + cameraX;
            let worldY = y + cameraY;
            if (worldY >= 0 && worldY < worldHeight && worldX >= 0 && worldX < worldWidth) {
                let tile_id = tileMap[worldY][worldX];
                ctx.drawImage(TILES[tile_id], x * tileWidth, y * tileHeight);
            }
            // ctx.fillText('🥷', x * tileWidth + 4, y * tileHeight + 24);
        }
    }
    ctx.font = '16px monospace';
    for (let y = 1; y < 1 + messageBuffer.length; y++) {
        ctx.fillText(messageBuffer[y - 1], 0, viewportHeight * tileHeight + 16 * y);
    }
}

window.addEventListener('load', () => {
    renderViewport(0, 0);
});

var cameraX = 0;
var cameraY = 0;

document.addEventListener('keydown', (e) => {
    if (e.key == "8") {
        cameraY--;
    } else if (e.key == "2") {
        cameraY++;
    } else if (e.key == "4") {
        cameraX--;
    } else if (e.key == "6") {
        cameraX++;
    }
    renderViewport(cameraX, cameraY);
});

// ---

// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:8765');

// Connection opened
socket.addEventListener('open', function (event) {
    socket.send('Hello Server!');
});

// Listen for messages
socket.addEventListener('message', function (event) {
        log(event.data);
});
