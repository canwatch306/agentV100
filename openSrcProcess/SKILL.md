---
name: git-fetch-extract
description: 从远端 Git 仓库的指定分支下载代码，并将仓库中 /drv 目录下的所有压缩文件解压到当前目录下的 output 目录（或用户指定的其他目录）。当需要从 Git 获取代码并解压多个压缩包时使用。
---

# Git 代码下载与解压（支持所有压缩文件）

从远端 Git 仓库克隆指定分支的代码，然后自动定位仓库内的 `/drv` 目录，将该目录下的所有压缩文件（如 `.tar.gz`, `.zip` 等）解压到**当前目录下的 `output` 目录**（或用户指定的其他目录）。该技能封装了 Git 操作和解压逻辑，避免代理手动执行复杂命令。

## 工作流程（检查清单）

- [ ] **步骤 1：确认参数** – 用户需提供 Git 仓库 URL 和分支名（可选，默认 `main`）。可指定目标解压目录（默认当前目录下的 `output`）。
- [ ] **步骤 2：执行脚本** – 运行 `python scripts/fetch_and_extract.py <repo_url> [--branch <branch>] [--target <target_dir>]`。
- [ ] **步骤 3：监控输出** – 脚本会打印克隆进度和解压状态，若出错会输出错误信息并退出。
- [ ] **步骤 4：验证结果** – 检查 `output` 目录（或指定目录）下是否生成了所有压缩包的解压内容。

## 注意事项（Gotchas）

- **Git 依赖**：系统必须安装 Git，且 `git` 命令在 PATH 中可用。
- **磁盘空间**：克隆仓库会占用额外空间，解压后原仓库可手动删除，但脚本不会自动清理。
- **分支名**：若分支名包含特殊字符（如 `/`），需确保正确转义。脚本使用 `git clone --branch <branch>`，支持普通分支名。
- **压缩格式支持**：脚本支持 `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2`, `.tar.xz`, `.txz`, `.zip`。其他格式（如 `.7z`）需要使用外部工具，脚本会给出提示。
- **跨平台解压**：使用 Python 标准库，在 Windows/Linux 下均可工作。

## 脚本使用

### `fetch_and_extract.py`

从 Git 仓库下载代码并解压 `/drv` 下的所有压缩文件。

**用法**：
```bash
python scripts/fetch_and_extract.py <repo_url> [--branch <branch>] [--target <target_dir>]