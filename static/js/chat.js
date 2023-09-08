var socket = io.connect('http://' + document.domain + ':' + location.port);
var currentReceiverId = null;


socket.on('new_message', function(data) {
    var messageContainer = document.createElement('div');

    // 检查发送方是否是当前用户
    if (String(data.sender_id) === String(userId)) {
        messageContainer.className = "message sent";
    } else {
        messageContainer.className = "message received";
    }
 
    var p = document.createElement('p');
    p.textContent = data.message;
    
    messageContainer.appendChild(p);
    document.getElementById('chat-messages').appendChild(messageContainer);
});

function sendMessage() {
    var input = document.getElementById('message');
    var receiverId = currentReceiverId
    socket.emit('new_message', {message: input.value, receiver_id: receiverId});

    var messageContainer = document.createElement('div');
    messageContainer.className = "message sent"
    var p = document.createElement('p');
    p.textContent = input.value;
    messageContainer.appendChild(p);
    input.value = '';
}

$(document).ready(function() {
    $(".friend-item").click(function() {
        // 从data-id属性中获取receiverId并存储到全局变量中
        currentReceiverId = $(this).attr('data-id');
    });
});

function loadChat(friendId) {
    $.ajax({
        url: "/getChatHistory",
        data: { "friend_id": friendId },
        type: "GET",
        dataType: "json",
        success: function(response) {
            // 清空当前聊天记录
            $(".chat-messages").empty();

            // 加载新的聊天记录
            for (let message of response.messages) {
                let messageType = message.sent_by_me ? "sent" : "received";
                $(".chat-messages").append(
                    `<div class="message ${messageType}"><p>${message.content}</p></div>`
                );
            }
        },
        error: function(error) {
            console.log(error);
        }
    });
}