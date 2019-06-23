var parent = document.querySelector('tbody');
var childs = document.querySelectorAll('tr.el-table__row');

childs.forEach(function (item) {
    if (item.querySelector('td.el-table_1_column_11 > div').innerText === "已取消") {
        parent.removeChild(item);
    }
})


// 用法：
// 将本段代码保存为小标签
// 即：
// javascript: 代码