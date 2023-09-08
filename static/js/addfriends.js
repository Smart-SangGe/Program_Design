$(document).ready(function() {
    var isModalOpen = false;

    // 当点击添加好友按钮时
    $(".add-friend-btn").click(function() {
        if (isModalOpen) {
            $("#searchModal").hide();  // 关闭模态窗口
            isModalOpen = false;
        } else {
            $("#searchModal").show();  // 显示模态窗口
            isModalOpen = true;
        }
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



