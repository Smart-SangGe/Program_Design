function comfirmDeleteFriend(friendId) {
    $.post("/comfirmDeleteFriend", { friendId: friendId }, function(data) {
        if (data.status === "success") {
            alert(data.message);
            location.reload();  // 刷新页面
        } else {
            alert(data.error);
        }
    });
}