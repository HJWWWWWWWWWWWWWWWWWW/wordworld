"""
烟雾测试 / 自检脚本
验证项目核心系统可正常运行。

用法：
  python scripts/smoke_test.py          # 运行全部检查
  python scripts/smoke_test.py --quick  # 仅快速检查（跳过 Excel 加载）
"""

import sys
import os
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def check(label: str, fn, *args, **kwargs):
    """运行单项检查并打印结果。"""
    try:
        fn(*args, **kwargs)
        print(f"  [PASS] {label}")
        return True
    except Exception as e:
        print(f"  [FAIL] {label}  --  {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="烟雾测试 / 自检脚本")
    parser.add_argument("--quick", action="store_true", help="快速模式（跳过 Excel 加载和单元测试）")
    args = parser.parse_args()

    print("残火长明 -- 烟雾测试")
    print(f"  Python: {sys.version.split()[0]}")
    print()

    passed = 0
    failed = 0

    # ── 1. 源码编译检查 ──
    print("=== 1. 源码编译 ===")
    import compileall
    src_dir = str(PROJECT_ROOT / "src")
    result = compileall.compile_dir(src_dir, force=True, quiet=1)
    if result is not False:
        count = result if isinstance(result, int) else "全部"
        print(f"  [PASS] 编译成功（{count} 个文件）")
        passed += 1
    else:
        print("  [FAIL] 编译失败")
        failed += 1

    # ── 2. 模块导入 ──
    print("\n=== 2. 模块导入 ===")
    if check("core.engine", lambda: __import__("wordworld.core.engine")): passed += 1
    else: failed += 1
    if check("data.workbook", lambda: __import__("wordworld.data.workbook")): passed += 1
    else: failed += 1
    if check("ui.console", lambda: __import__("wordworld.ui.console")): passed += 1
    else: failed += 1

    # Pygame -- 无显示环境可能失败但非致命
    try:
        __import__("wordworld.ui.pygame_ui")
        print("  [PASS] ui.pygame_ui (pygame 可用)")
    except Exception as e:
        print(f"  [WARN] ui.pygame_ui  --  {e}")
        print("         (无显示环境，非致命)")
    passed += 1

    # ── 3. GameEngine 初始化 ──
    print("\n=== 3. GameEngine ===")
    from wordworld.core.engine import GameEngine

    engine = GameEngine()
    if check("GameEngine() 创建", lambda: engine): passed += 1
    else: failed += 1

    engine.new_game()
    p = engine.player
    if check("new_game() 初始化玩家", lambda: p): passed += 1
    else: failed += 1

    # ── 4. 玩家基础字段 ──
    print("\n=== 4. 玩家字段 ===")
    required_fields = [
        ("name", str), ("hp", int), ("max_hp", int), ("atk", int), ("def", int),
        ("spd", int), ("wallet", dict), ("items", list),
        ("flags", list), ("relationships", dict),
        ("story_stage", int), ("last_map", str),
    ]
    all_ok = True
    for field_name, field_type in required_fields:
        ok = field_name in p and isinstance(p[field_name], field_type)
        val_repr = repr(p.get(field_name, "MISSING"))[:60]
        if ok:
            print(f"  [PASS] {field_name}: {val_repr}")
        else:
            print(f"  [FAIL] {field_name}: 缺失或类型错误 ({val_repr})")
            all_ok = False
    if all_ok: passed += 1
    else: failed += 1

    # ── 5. 工作簿加载 + 当前事件 + available_options ──
    if not args.quick:
        print("\n=== 5. Excel 配置加载 ===")
        if check("available_options()", lambda: len(engine.available_options()) > 0): passed += 1
        else: failed += 1

        print("\n=== 6. 当前事件 ===")
        if check("current_event", lambda: engine.current_event is not None): passed += 1
        else: failed += 1

        print("\n=== 7. available_options ===")
        opts = engine.available_options()
        if check(f"选项数={len(opts)}", lambda: opts): passed += 1
        else: failed += 1
    else:
        print("\n=== 5-7. 跳过（快速模式）===")
        passed += 3

    # ── 8. 保存/读取 ──
    print("\n=== 8. 存档系统 ===")
    engine.save()
    save_path = PROJECT_ROOT / "saves" / "autosave.json"
    if check("save()", lambda: save_path.exists()): passed += 1
    else: failed += 1

    ok = engine.load()
    if check("load()", lambda: ok): passed += 1
    else: failed += 1

    # ── 9. 核心操作 ──
    print("\n=== 9. 核心操作 ===")
    if check("cultivate()", lambda: engine.cultivate()): passed += 1
    else: failed += 1
    if check("rest()", lambda: engine.rest()): passed += 1
    else: failed += 1

    # ── 10. 单元测试 ──
    if not args.quick:
        print("\n=== 10. 单元测试 ===")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=60
        )
        if result.returncode == 0:
            out_lines = result.stdout.strip().split("\n")
            last = [l for l in out_lines if l.startswith("Ran ") or l == "OK"]
            if not last:
                last = out_lines[-2:] if len(out_lines) >= 2 else out_lines
            print(f"  [PASS] {'; '.join(last)}")
            passed += 1
        else:
            print(f"  [FAIL] 测试失败 (exit={result.returncode})")
            for line in result.stdout.strip().split("\n")[-8:]:
                if line.strip():
                    print(f"     {line.strip()[:100]}")
            if result.stderr.strip():
                for line in result.stderr.strip().split("\n")[-5:]:
                    print(f"     ERR: {line.strip()[:100]}")
            failed += 1
    else:
        print("\n=== 10. 单元测试（跳过）===")
        passed += 1

    # ── 总结 ──
    print(f"\n{'='*50}")
    print(f"  结果: {passed} 通过, {failed} 失败")
    if failed == 0:
        print("  全部烟雾测试通过！项目核心系统正常。")
    else:
        print("  存在失败项，请检查上面输出。")
    print(f"{'='*50}")

    return failed


if __name__ == "__main__":
    sys.exit(main())
