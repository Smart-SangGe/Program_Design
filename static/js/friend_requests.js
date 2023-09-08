function acceptRequest(requestId) {
    $.post("/acceptFriendRequest", { requestId: requestId }, function(data) {
        if (data.status === "success") {
            alert(data.message);
            location.reload();  // 刷新页面
        } else {
            alert(data.error);
        }
    });
}

function rejectRequest(requestId) {
    $.post("/rejectFriendRequest", { requestId: requestId }, function(data) {
        if (data.status === "success") {
            alert(data.message);
            location.reload();  // 刷新页面
        } else {
            alert(data.error);
        }
    });
}