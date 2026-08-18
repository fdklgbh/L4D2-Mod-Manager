# AGENTS.md

## 适用范围

本文件适用于整个仓库。执行任务时，以用户当前明确要求为最高优先级；若本文件与更具体目录中的 `AGENTS.md` 冲突，则更具体目录的规则优先。

## 项目概况

- 项目名称：L4D2 Mod Manager（求生之路 2 模组管理器）。
- 技术栈：Python 3.12.11、PySide6、PySide6-Fluent-Widgets、Pydantic、Alembic、Loguru。
- 依赖与虚拟环境由 `uv` 管理，依赖声明位于 `pyproject.toml`，锁文件为 `uv.lock`。
- 应用入口为 `src/main.py`。
- 源码采用 feature-oriented 布局，架构决策见 `docs/decisions/001-feature-oriented-layout.md`。

## 目录职责

- `src/features/<feature>/`：功能页面及其专属对话框、Qt 模型、worker 和 UI 文件。
- `src/shared/`：可复用的配置、持久化、领域模型、运行时、VPK、UI 和通用组件；禁止依赖 `src/features/`。
- `src/shell/main_window.py`：只负责组合功能页面和应用导航。
- `src/resources/`：Qt 资源、图标和样式。
- `alembic/`：数据库迁移。
- `scripts/`：项目维护脚本。
- `docs/decisions/`：架构决策记录。

## 常用命令

在仓库根目录执行：

```powershell
uv sync
uv run python src/main.py
uv run ruff check .
uv run ruff format --check .
uv run pre-commit run --all-files
```

创建 Alembic 自动迁移时使用：

```powershell
uv run python scripts/revision.py "迁移说明"
```

数据库结构变更及迁移文件生成必须得到任务明确授权。

## 编码与实现约定

- 对应页面的 DB 类只负责数据的增删改查（CRUD）及必要的数据映射，禁止在 DB 类中处理业务逻辑、页面交互或业务流程编排；相关逻辑应由上层调用方负责。
- 所有新增或修改的文本文件必须使用 UTF-8 编码。
- Python 代码以 3.12 为目标版本，遵循 `pyproject.toml` 中的 Ruff 配置，行宽上限为 88。
- 修改前先阅读相关文件，并优先沿用现有模块、命名、导入、Qt 信号槽和错误处理模式。
- 新页面或独立功能放入对应的 `src/features/<feature>/`；仅真正跨功能复用的代码放入 `src/shared/`。
- `src/shared/` 不得导入任何 feature；功能间共享逻辑应下沉到职责明确的 shared 模块。
- 只做完成当前任务所需的最小改动，不顺带重构无关代码，不修改生成物或依赖锁文件，除非任务确实需要。
- 不静默改变数据库迁移、用户配置、模组文件移动或 VPK 写入行为；涉及数据损失风险时必须先说明并确认。
- 注释只解释不直观的约束、原因或边界，不复述代码本身。
- 代码中注释风格，统一用google注释风格，注释内容用中文描述
- 禁止在销毁后的组件中去获取数据或者对象


## 测试规则

- 除非用户或任务明确要求编写、补充、修改或删除测试用例，否则不要改动任何测试代码，也不要新增测试文件。
- 未要求编写测试用例时，可以按改动风险运行已有测试、Ruff 或其他现有检查进行验证；验证失败时应如实报告，不得通过删除或弱化测试规避失败。

## Git 与文件边界

- 禁止修改本项目目录以外的文件或文件夹。
- 未经用户明确允许，禁止对 Git 远程仓库执行 push、pull、fetch、创建 PR、修改分支等操作。
- 保留工作区中已有的用户改动；不要执行 `git reset --hard`、`git checkout --` 或其他可能覆盖未提交内容的命令。
- 不提交密钥、令牌、个人路径、运行时数据、日志或其他敏感信息。

## 执行原则

- 对需求中的歧义，先从现有代码、配置和文档中寻找依据；会显著影响行为且无法可靠判断时，再向用户确认。
- 对明显不合理、危险或与项目约束冲突的要求，应拒绝执行并说明原因，除非用户在了解风险后明确强制要求且该操作仍可安全实施。
- 完成任务后说明实际改动、执行过的验证，以及因环境或授权限制未执行的检查。
