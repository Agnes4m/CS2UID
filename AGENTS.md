# CS2UID 项目说明

## 项目简介
基于 gsuid_core 的 CS2 游戏机器人插件,支持多平台 Bot 适配(OneBot/QQ/微信/KOOK/Telegram/Discord 等)。

## 目录结构
- `CS2UID/csgo_info/` — 用户信息查询(查询/库存/对局记录/搜索)
- `CS2UID/csgo_user/` — 用户登录、绑定、添加 TK/SK
- `CS2UID/csgo_help/` — 帮助图与指令注册
- `CS2UID/csgo_items/` — 道具教学(地图点位/烟雾弹/闪光弹)
- `CS2UID/csgo_download/` — 资源下载
- `CS2UID/csgo_status/` — 插件状态
- `CS2UID/utils/api/` — 平台 API(完美/5E)+ 性能优化
- `CS2UID/utils/database/` — 数据库模型(CS2Bind/CS2User)
- `tests/` — 单元测试

## 工程规范

### 包管理 / 依赖
- **强制使用 uv**(不要用 python3 / pip 直接操作)
- `pyproject.toml` 使用 PEP 621 格式,不再使用 `[tool.poetry]`
- Python 目标版本: **3.12+**(`pyproject.toml: requires-python = ">=3.12"`,与 gsuid-core 对齐)
- 本地 gsuid-core 源:`[tool.uv.sources] gsuid-core = { path = "/home/jxhh/Apps/gsuid_core", editable = true }`

### 代码风格 / Lint
- **强制使用 ruff**(已替代 black/isort/flake8)
- 配置在 `[tool.ruff]` 段:`line-length = 79`、`target-version = "py312"`
- 启用的规则集:`E`/`W`/`F`/`I`/`B`/`UP`/`SIM`
- pre-commit 钩子已配置 `ruff` + `ruff-format`,提交前会自动跑

### 类型注解
- 严格使用 PEP 604 (`X | Y`) / PEP 585 (`dict[str, int]`) 写法
- 所有公共 API 必须有完整签名
- 内部函数可以宽松

### 平台判断
- 用户输入文本解析平台走 `CS2UID/utils/platform.py:resolve_uid_and_platform`
- 不要在 handler 里直接 `if "5E" in text` 等手写判断
- 平台字面量使用 `"pf"` / `"5e"` / `"gf"`(不要用 `"官匹"`/`"完美"`)

### 错误码
- API 调用结果统一封装为 `Result = dict | int`,`int` 表示错误码
- 使用 `CS2UID/utils/error_reply.py:get_error` 翻译错误码为人类语言

### 日志
- 生产路径(API 响应体)走 `safe_log_response` 自动脱敏
- 日志级别:正常请求响应 → `debug`,错误 → `warning`/`error`

### 测试
- 测试统一放 `tests/`,使用 pytest + pytest-asyncio
- 新增可复用工具时,必须在 `tests/` 下加单元测试
- 命名:`tests/test_<module>.py`
- 已覆盖:`platform`、`safe_log`、`cache`、`perf`、`error_reply`、`api` 端点、`csgo_info/utils`

### 业务常量
- 对局类型映射(`天梯`/`pro`/`巅峰`/`周末`/`自定义` → tag)集中在 `CS2UID/utils/csgo_config.py:DEFAULT_MATCH_TYPES`
- 新增/调整走 `csgo_config.get_match_types()`,不要在 handler 里写死字典

### 性能
- HTTP 请求统一走 `utils/api/perf/pool.py:ConnectionPool`(HTTP/2 + keepalive)
- 缓存使用 `utils/cache.py:cs2_cache`(内存 TTL)
- 同 key 并发请求走 `utils/api/perf/coalescer.py:RequestCoalescer`

### 数据库
- 所有平台迁移 SQL 放 `utils/database/migrations.sql`,由 `database/models.py` 加载
- 不要直接在 `exec_list.append` 里写 `ALTER TABLE`

## 常用命令
```bash
uv sync                  # 安装依赖
uv run pytest tests/     # 跑测试
uv run ruff check .      # lint
uv run ruff format .     # format
```
