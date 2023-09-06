document.getElementById('logout-btn').addEventListener('click', function(e) {
    if (!confirm('确定要退出登录吗？')) {
        e.preventDefault();  // 阻止默认的按钮行为
    }
});
