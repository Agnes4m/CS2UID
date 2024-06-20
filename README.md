# CS2UID

<p align="center">
  <a href="https://github.com/Agnes4m/CS2UID"><img src="https://github.com/Agnes4m/CS2UID/blob/main/img/logo.jpg" width="256" height="256" alt="CS2lUID"></a>
</p>
<h1 align = "center">CS2UID 0.1</h1>
<h4 align = "center">🚧支持QQ群/频道、OneBot、微信、KOOK、Tg、飞书、DoDo、~~米游社~~、Discord的CS2 bot插件🚧</h4>
<div align = "center">
        <a href="http://docs.gsuid.gbots.work/#/" target="_blank">安装文档</a>
</div>


## 丨安装提醒

> **注意：该插件为[早柚核心(gsuid_core)](https://github.com/Genshin-bots/gsuid_core)的扩展，具体安装方式可参考[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)**
>
> 支持NoneBot2 & HoshinoBot & ZeroBot & YunzaiBot & Koishi的CS2(原名CSGO)游戏Bot插件
>
> 🚧暂时功能不全，等待施工中...🚧

## 丨安装方式

方法一：指令`core安装插件CS2UID`

<details><summary>方法二： 手动安装</summary><p>

```bash
cd gsuid_core
cd plugins

# 安装CS2UID
git clone https://github.com/Agnes4m/CS2UID.
# 返回主目录
cd ../

# 启动Bot（如此时GsCore正在运行，请先使用Ctrl+C快捷键关闭GsCore，无需重启Bot（如NoneBot2））
poetry run core
```
</p></details>


## 丨功能

- 绑定切换删除UID - 命令:csgo绑定UID、csgo删除UID、csgo切换UID</

- <details><summary>查询基本信息 - 命令: csgo查询</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test1.jpg"><img src="https://github.com/Agnes4m/CS2UID/blob/main/img/test1.png" width="360" height="800" alt="CS2lUID_查询"></a>
</p></details>

- <details><summary>查询官匹基本信息 - 命令: csgo查询官匹</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test2.jpg"><img src="https://github.com/Agnes4m/CS2UID/blob/main/img/test2.png" width="360" height="800" alt="CS2lUID_官匹"></a>
</p></details>

- <details><summary>查询steam库存 - 命令: csgo库存</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test3.jpg"><img src="https://github.com/Agnes4m/CS2UID/blob/main/img/test3.png" width="360" height="800" alt="CS2lUID_库存"></a>
</p></details>

- 查询好友码 - 命令: csgo好友码

### 管理员功能

- 添加TK/uid（私聊） - 命令: csgo添加tk|csgo添加uid


## 丨使用方式

1. 安装插件
2. 使用**小号**打开**完美对战平台**
3. 打开Fiddler或者其他抓包软件，抓取**pwasteamid**和**access_token**
   1. host为`pwaweblogin.wmpvp.com`的请求
   2. 部分Cookie中**steam_cn_token**的值是等同**access_token**的值的

4. 私聊Bot，发送`csgo添加uid|tk` ，并在**命令后面直接**附上你第三步获取到的**pwasteamid**和**access_token**
   1. `csgo添加uid 4000****4000`
   2. `csgo添加tk 1e15****f5w8`
   3. 如果不添加则无法使用csgo指令查询

5. 可以正常使用Bot了！
   1. 首先需要知道自己的uid，也就是steam64位id,上述抓包的**pwasteamid**就是当前账户uid，也可以通过steam或者完美平台个人信息自行查询
   2. 发送`csgo绑定uid`
   3. 可以进行查询，使用`csgo查询`进行查询即可

## 丨获取uid的方法（为啥这么多玩cs的都不知道steam id）

方法1. steam打开个人资料，右击复制url，最后的一长串数字就是uid
方法2. pc完美对战平台个人资料，steam64位id
方法3. 手机app完美对战平台，左上三横线-设置-我的账号-steam账号-64位id
方法4. 抓包

## 丨待做功能

1. 搜索steam/完美平台用户昵称获取uid
2. 获取对战记录详情数据
3. 优化图片
4. 获取5e对~~转~~站平台战绩
5. 其他想不到了

## 丨其他

+ 本项目仅供学习使用，请勿用于商业用途
+ 喜欢可以点个star，欢迎大佬pr支持本项目
+ [常见问题](question.md)
+ 头像和图片来自完美平台CS虚拟主播[永恒娘](https://b23.tv/DKblgCH)，侵删
+ [GPL-3.0 License](https://github.com/qwerdvd/StarRailUID/blob/master/LICENSE)
