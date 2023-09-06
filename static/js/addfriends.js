$(document).ready(function() {
    $(".add-friend-btn").click(function() {
        $.post("/addfriends", {}, function(data) {
            if (data.status === "success") {
                alert(data.message);
            } else {
                alert("添加失败");
            }
        });
    });
});

$(document).ready(function() {
    // 当点击添加好友按钮时，显示搜索框
    $(".add-friend-btn").click(function() {
        $("#searchModal").show();
    });

    // 当点击发送请求按钮时
    $("#sendRequest").click(function() {
        let friendUsername = $("#friendUsername").val();

        // 使用 AJAX 发送好友请求
        $.post("/sendFriendRequest", { username: friendUsername }, function(data) {
            if (data.status === "success") {
                alert(data.message);
                $("#searchModal").hide();  // 关闭模态窗口
            } else {
                alert(data.error);
            }
        });
    });
});



