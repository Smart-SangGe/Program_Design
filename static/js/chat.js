var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('new_message', function(data) {
    var li = document.createElement('li');
    li.textContent = data.message;
    document.getElementById('messages').appendChild(li);
});

function sendMessage() {
    var input = document.getElementById('message');
    socket.emit('send_message', {message: input.value});
    input.value = '';
}

function loadChat(friendId) {
    $.ajax({
        url: "/get_chat_history",
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