# 更新日志
## 2023/12/18 目前漫画平台机制修改，本工具已经不能正常使用，后续有空更新
- [ 拷贝漫画下载器食用说明](#head1)
  - [step1. 确保你的windows电脑安装了chrome浏览器](#head2)
  - [step2.  下载适合你的chrome浏览器版本的驱动程序](#head3)
  - [step3. 解压chromedriver.exe驱动文件到特定目录](#head4)
  - [step4. 将驱动文件目录放到用户/系统环境变量下](#head5)
  - [step 5. 双击main.exe使用(允许程序使用网络)](#head6)



# <span id="head1"> 拷贝漫画下载器食用说明</span>

## <span id="head2">step1. 确保你的windows电脑安装了chrome浏览器</span>

如没有，在下面地址下载安装：

https://www.google.cn/intl/zh-CN/chrome/



## <span id="head3">step2.  下载适合你的chrome浏览器版本的驱动程序</span>

根据你的chrome浏览器版本（在下图位置找到）：

<img src="https://github.com/Holy-Shine/copymanga-downloader/blob/main/img/1.png">

去下面的网站下载驱动程序：

http://chromedriver.storage.googleapis.com/index.html

> 尽量选择与你的浏览器版本一致的驱动，最后几位数字可以不同
>
> 选择后缀名为`win32`的压缩包下载，里面是一个名为**chromedriver.exe**的可执行驱动文件

<img src="https://github.com/Holy-Shine/copymanga-downloader/blob/main/img/2.png">

## <span id="head4">step3. 解压chromedriver.exe驱动文件到特定目录</span>

- 新建一个全英文路径的文件夹，例如: `D:\Software\chrome_driver\`
- 将上面压缩包中的**chromedriver.exe**解压到目录中
- 最终路径为`D:\Software\chrome_driver\chromedriver.exe`



## <span id="head5">step4. 将驱动文件目录放到用户/系统环境变量下</span>

<img src="https://github.com/Holy-Shine/copymanga-downloader/blob/main/img/3.png">

1. 搜索or控制面板找到环境变量
2. 点击【环境变量】
3. 选中用户栏中的【PATH】，双击打开“编辑环境变量对话框”
4. 新建or双击底部空白位置，将刚才的驱动目录输入，如图③所示
5. 点击确定
6. 重启电脑



## <span id="head6">step 5. 双击main.exe使用(允许程序使用网络)</span>
考虑到信息展示问题，推荐使用**windows powershell**在`main.exe`目录下打开，然后执行
```
.\main.exe
```

## 备注
1. 如果下载遇到错误，请尝试关闭电脑的代理工具，再重新打开软件
