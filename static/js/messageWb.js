const currentUrl = window.location.href;
const chatType = currentUrl.split('/')[4];
const chatUsername = currentUrl.split('/')[6];
const singleChat = currentUrl.split('/')[5];

const group = (singleChat === 'single-chat') ? '' : '-group'

const urlwb = `ws://127.0.0.1:8000/websocket/${ chatType }${ group }/${ chatUsername }`;
const chat_websocket = new WebSocket(urlwb);
const sendBTN = document.getElementById('sendButton');
const textData = document.getElementById('text-data');
const fileInput = document.getElementById('file-input');
const chatArea = document.getElementsByClassName('chat-area-main')[0];

const newMessage = chatArea.lastElementChild;
if (newMessage) newMessage.scrollIntoView({ behavior: "smooth" });

function convertFileToBase64(file) {
return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
    const base64String = reader.result.split(",")[1];
    resolve(base64String);
    };
    reader.onerror = error => reject(error);

    reader.readAsDataURL(file);
});
}

sendBTN.addEventListener('click', async () => {
let message = textData.value;
let fileContent = fileInput.files[0];
let upLoadedFile = null;

if ( message || fileContent ) {
    const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    });

    async function Main() {
    try {
        upLoadedFile = await toBase64(fileContent);
        data = {
        type: "message",
        message: message,
        file: upLoadedFile,
        };
        chat_websocket.send(JSON.stringify(data));
        textData.value = '';
    } catch(error) {
        console.error(error);
        return;
    }
    }
    
    if (fileContent) {
    Main();
    } else {
    data = {
        type: "message",
        message: message,
    };
    chat_websocket.send(JSON.stringify(data));
    textData.value = '';
    }
    
}
});

chat_websocket.onmessage = (event) => {
let data = JSON.parse(event.data);
let type = data.type;

if (type === 'online_status_handler') {
    let online = data.online_members;
    let oMC = document.getElementById('online-members-count');
    oMC.innerHTML = online + ' online';

} else if (type === 'receiver') {
    let message = data.message;
    chatArea.insertAdjacentHTML("beforeend", message);

    const newMessage = chatArea.lastElementChild;
    newMessage.scrollIntoView({ behavior: "smooth" });
}
};
