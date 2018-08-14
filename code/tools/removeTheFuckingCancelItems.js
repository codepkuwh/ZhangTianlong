var parent = document.querySelector("table tbody");
var childs = document.querySelectorAll("tr[style='background: #F8F8F8;']");

childs.forEach(function (item) {
    parent.removeChild(item);
})


// 用法：
// 将本段代码保存为小标签
// 即：
// javascript: 代码