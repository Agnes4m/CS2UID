-- CS2UID 数据库迁移 SQL
-- 通过 gsuid_core.utils.database.startup.exec_list 在启动时按顺序执行
-- 新增语句请追加到末尾,不要修改历史语句(已部署用户的库会重复执行旧语句)

-- v0.2.0: 完善绑定表
ALTER TABLE CS2Bind ADD COLUMN platform TEXT DEFAULT "pf";
ALTER TABLE CS2Bind ADD COLUMN domain TEXT DEFAULT "";
