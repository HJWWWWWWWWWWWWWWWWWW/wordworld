# 打包指南

## Windows .exe 打包（PyInstaller）

### 安装

```bash
pip install pyinstaller
```

### 打包命令

```bash
# 单文件打包（推荐）
pyinstaller --onefile --windowed run_pygame.py --name CanhuoChangming

# 如需包含数据文件
pyinstaller --onefile --windowed run_pygame.py --name CanhuoChangming --add-data "story;story" --add-data "src;src"
```

### 产物位置

- `dist/CanhuoChangming.exe` — 可分发的单文件
- `build/` — 临时构建文件（不提交到 Git）
- `*.spec` — PyInstaller 配置文件

### 注意事项

- 打包前确保 `python run_pygame.py` 可正常运行
- 打包后需在有 `story/` 目录的环境下运行（如未内嵌数据）
- `dist/`、`build/`、`*.spec` 已在 `.gitignore` 中排除
- 正式发布时上传到 GitHub Release，不提交源码仓库

## 其他平台

### macOS

```bash
pyinstaller --onefile --windowed run_pygame.py --name CanhuoChangming
```

### Linux

```bash
pyinstaller --onefile run_pygame.py --name CanhuoChangming
```

## 发布建议

- [itch.io](https://itch.io) — 独立游戏发布平台
- [GitHub Release](https://github.com/HJWWWWWWWWWWWWWWWWWW/wordworld/releases) — 源码 + 打包产物
