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