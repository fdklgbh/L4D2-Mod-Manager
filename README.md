# L4D2 Mod Manager

求生之路2 模组管理器
![img.png](readme_pic/mod页面.png)
![img.png](readme_pic/mod页面选中mod.png)
![img.png](readme_pic/mod页面右键菜单.png)
![img.png](readme_pic/设置页.png)
## 1.0.1

**优化**

1. 增加快捷键
    1. 刷新 F5
    2. 搜索 Ctrl+F
2. 列表选中其中一个后,右侧展示信息可拖动隐藏
3. 增加多个文件一起禁用启用
4. 筛选分类或者搜索后,移动文件后,操作后还存在数据,不会复原
5. addonsinfo文件不存在会把文本信息控件隐藏
6. 新增更新日志

**修复问题**

1. vpk文件打开成功,读取vpk文件路径,编码错误
2. 配置禁用目录后,不会自动创建

### 在原有基础上继续编写需要的操作

1. 本地拉源代码继续写,需要先拉[my_qfluent_utils_package](https://github.com/fdklgbh/my_qfluent_utils_package.git)
2. 进入对应python环境以及进入仓库路径执行package.bat