from gsuid_core.utils.database.startup import exec_list

exec_list.append('ALTER TABLE CS2Bind ADD COLUMN platform TEXT DEFAULT "pf"')
exec_list.append('ALTER TABLE CS2Bind ADD COLUMN domain TEXT DEFAULT ""')
