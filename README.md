<!-- markdownlint-disable MD033 -->
# CS2UID

<p align="center">
  <a href="https://github.com/Agnes4m/CS2UID"><img src="./img/logo.jpg" width="256" height="256" alt="CS2lUID"></a>
</p>
<h1 align = "center">CS2UID 0.2.0</h1>
<h4 align = "center">🚧支持QQ群/频道、OneBot、微信、KOOK、Tg、飞书、DoDo、米游社、Discord的CS2 bot插件🚧</h4>
<div align = "center">
        <a href="http://docs.gsuid.gbots.work/#/" target="_blank">安装文档</a>
</div>

## 丨安装提醒

> **注意：该插件为[早柚核心(gsuid_core)](https://github.com/Genshin-bots/gsuid_core)的扩展，具体安装方式可参考[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)**
>
> 支持NoneBot2 & HoshinoBot & ZeroBot & YunzaiBot & Koishi的CS2(原名CSGO)游戏Bot插件

## 注意

**现已将指令`csgo`改为`cs`**

+ [常见问题](question.md)

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

## 丨功能 (全部指令见帮助指令内)

绑定切换删除UID - 命令:cs绑定UID、cs删除UID、cs切换UID、cs绑定UID5e、cs删除UID5e、cs切换UID5e</

帮助 - 命令: cs帮助

<details><summary>查询基本信息 - 命令: cs查询</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test1.jpg"><img src="./img/test1.png" width="360" height="800" alt="CS2lUID_查询"></a>
</p></details>

<details><summary>查询官匹基本信息 - 命令: cs查询官匹</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test2.jpg"><img src="./img/test2.png" width="360" height="800" alt="CS2lUID_官匹"></a>
</p></details>

<details><summary>查询steam库存 - 命令: cs库存</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test3.jpg"><img src="./img/test3.png" width="360" height="800" alt="CS2lUID_库存"></a>
</p></details>

查询好友码 - 命令: cs好友码

搜索用户 - 命令: cs搜索 + name

<details><summary>查询对局记录信息 - 命令: cs对局记录</summary><p>
<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test4.jpg"><img src="./img/test4.png" width="360" height="800" alt="CS2lUID_对局信息"></a>
</p></details>

<details><summary>查询地图道具点位 - 命令: cs道具</summary><p>

+ 参数以空格间隔，参数数量为0-4
+ 如果参数为0，返回地图
+ 如果参数为1，地图存在返回地图开始点位
+ 如果参数为2，地图存在返回地图目的点位
+ 如果参数为3且最后一个参数是道具(火/烟/闪/雷),则默认开始点位和目的点位一致
+ 如果参数为4，则正常输出攻略

<a href="https://github.com/Agnes4m/CS2UID/blob/main/img/test5.jpg"><img src="./img/test5.png"  alt="CS2lUID_道具"></a>
</p></details>

### 管理员功能

+ 添加TK/uid（私聊） - 命令: cs添加tk|cs添加uid

+ 下载拓展资源 - 命令: cs下载全部资源

## 丨使用方式

### 完美抓包

1. 安装插件
2. 使用**小号**打开**完美对战平台**
3. 打开Fiddler或者其他抓包软件，抓取**pwasteamid**和**access_token**
   1. host为`pwaweblogin.wmpvp.com`的请求
   2. 部分Cookie中**steam_cn_token**的值是等同**access_token**的值的

4. 私聊Bot，发送`cs添加uid|tk` ，并在**命令后面直接**附上你第三步获取到的**pwasteamid**和**access_token**
   1. `cs添加uid 4000****4000`
   2. `cs添加tk 1e15****f5w8`
   3. 如果不添加则无法使用cs指令查询

5. 可以正常使用Bot了！
   1. 使用`cs搜索`查询自己的64位steamid，也可以通过steam或者完美平台个人信息自行查询
   2. 发送`cs绑定uid + name`
   3. 可以进行查询，使用`cs查询`进行查询即可

### 5e抓包(仅安卓)

1. 安装插件
2. 使用**小号**打开**5e对战平台app**
3. 打开小黄鸟或者其他抓包软件，抓取**token**
   1. host为`app.5eplay.com`或`ya-api-app.5eplay.com`的请求
   2. 基本能抓到的包都有这个参数

4. 私聊Bot，发送`cs添加sk` ，并在**命令后面直接**附上你第三步获取到的**token**
   1. `cs添加sk WOSFNJX****`
   2. 如果不添加则无法使用`cs搜索`指令查询

5. 可以正常使用Bot了！
   1. 使用`cs搜索5e`查询自己的5e uid
   2. 发送`cs绑定uid5e + name`
   3. 可以进行查询，使用`cs查询5e`进行查询即可

## 丨当前进度

+ [x] 查询完美基本信息
+ [x] 查询官匹基本信息
+ [x] 查询steam饰品库存
+ [x] 查询好友码
+ [x] 查询完美平台对局记录
+ [x] 查询官匹对局记录
+ [x] 通过名称搜索用户
+ [x] 统一core的帮助图片
+ [x] 查询道具点位（目前完成7个地图，未完成地图包括小镇、新两图，以及改版后小镇和大厦点位）
+ [x] gs站资源图片下载
+ [x] 5e等其他平台战绩查询(目前遇到core架构问题读取不出来5e平台)

## 丨其他

+ 本项目仅供学习使用，请勿用于商业用途
+ 喜欢可以点个star，欢迎大佬pr支持本项目
+ [个人讨论交流群](https://jq.qq.com/?_wv=1027&k=HdjoCcAe), 如果iss没回复可以群里找
+ 头像和图片来自完美平台CS虚拟主播[永恒娘](https://b23.tv/DKblgCH)，侵删
+ [GPL-3.0 License](https://github.com/qwerdvd/StarRailUID/blob/master/LICENSE)
