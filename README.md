# 用于存放学习笔记、代码
# /code
## /tools
存放一些实用工具的代码

### removeTheFuckingCancelItems.js
移除1v1试听课页面中，取消试听的同学

### renameTo1v1.py
将录屏重命名，并移动到指定文件夹

### renameToPL.py
将录屏重命名，并移动到对应 level，对应节数，对应班级的文件夹中

### run_brook
包含两个文件：

1. brook.exe 
   一个翻墙软件，通过cmd调用
2. run_brook.py 
   自动爬虫可用代理，并运行 brook 的脚本，需要管理员权限（修改hosts)。会生成一个 log 文件。

用法：

  将两个文件放在同一目录下，运行 run_brook.py

### oneClick.py
用于一键上传教案、录屏、听课报告等（尚未完成）
TODO:

- [x] 登录
- [x] 识别录屏试讲并上传到服务器（但不能提交上传信息）
- [ ] 文件自动分类
- [ ] 文件上传
- [ ] 分析 Authorization 的组成部分
- [ ] doc 文件的上传
- [ ] 课堂录屏的上传

# /note
用于存放学习笔记
### tailRecurseOptimized.py
python实现的尾递归优化