let ws;
document.getElementById('connectForm').onsubmit = function (event) {
    event.preventDefault();
    connect();
};

function connect() {
    const username = document.getElementById('username').value;
    ws = new WebSocket(`ws://localhost:8000/ws/${username}`);
    ws.onopen = () => {
        console.log("Connected to WebSocket server");
    };
    ws.onmessage = (event) => {
        const messagesDiv = document.getElementById("messages");
        const message = document.createElement("div");
        message.textContent = event.data;
        messagesDiv.appendChild(message);
        const data = JSON.parse(event.data);
        if (data.type === "play") {
            playMusic(data.url);
        }
    };
}

function sendPlayCommand() {
    const input = document.getElementById("messageInput");
    const message = { type: "play", url: input.value };
    ws.send(JSON.stringify(message));
    input.value = '';
}

function playMusic(url) {
    const audioPlayer = document.getElementById("audioPlayer");
    const audioSource = document.getElementById("audioSource");
    audioSource.src = url;
    audioPlayer.load();
    audioPlayer.play();
}
