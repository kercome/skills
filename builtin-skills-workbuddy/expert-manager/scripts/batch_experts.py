#!/usr/bin/env python3
"""
Batch Expert Helper — 批量创建专家的示例脚本。

核心原则：每个专家必须串行执行，完整走 init → validate → register 标准流程。
本脚本作为模板，AI 编写批量脚本时必须遵循相同模式。

Usage:
    python3 scripts/batch_experts.py <batch-config.json> [--session-id <id>]

batch-config.json:
    {
      "path": "~/.workbuddy/plugins/marketplaces/my-experts/plugins",
      "experts": [
        { "name": "my-expert", "type": "agent" },
        { "name": "my-team", "type": "team" }
      ]
    }
"""

import sys
import json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def run_step(script_name: str, args: list) -> bool:
    """运行单个标准流程脚本，返回是否成功。"""
    cmd = [sys.executable, str(SCRIPT_DIR / script_name)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr.strip():
        print(result.stderr.strip())
    return result.returncode == 0


def process_one_expert(name: str, expert_type: str, output_dir: Path, session_id: str = None) -> bool:
    """
    单个专家的完整标准流程。
    每个专家必须经过：init → validate → register，缺一不可。
    """
    expert_path = str(output_dir / name)

    # Step 1: 初始化目录
    print(f"\n{'─'*40}")
    print(f"📦 [{name}] Step 1/3: 初始化")
    if not run_step('init_expert.py', [name, '--type', expert_type, '--path', str(output_dir)]):
        print(f"   ❌ 初始化失败，跳过该专家")
        return False

    # ═══════════════════════════════════════════════════════
    # Step 2: AI 填充内容（在实际使用中，这里由 AI 写入文件）
    # 本脚本仅做流程示例，不包含内容生成逻辑。
    # AI 在此步骤应写入 plugin.json、agents/*.md、 头像 等文件。
    # ═══════════════════════════════════════════════════════

    # Step 3: 校验
    print(f"📋 [{name}] Step 2/3: 校验")
    if not run_step('validate_expert.py', [expert_path]):
        print(f"   ❌ 校验失败，不予注册")
        return False

    # Step 4: 注册
    print(f"📝 [{name}] Step 3/3: 注册")
    register_args = [expert_path]
    if session_id:
        register_args.extend(['--session-id', session_id])
    if not run_step('register_expert.py', register_args):
        print(f"   ❌ 注册失败")
        return False

    print(f"   ✅ [{name}] 完成")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    config_path = Path(sys.argv[1]).resolve()
    session_id = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--session-id' and i + 1 < len(sys.argv):
            session_id = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    output_dir = Path(config.get('path', '~/.workbuddy/plugins/marketplaces/my-experts/plugins')).expanduser().resolve()
    experts = config.get('experts', [])

    if not experts:
        print("❌ 配置中无专家列表")
        sys.exit(1)

    print(f"🚀 批量创建 {len(experts)} 个专家 → {output_dir}\n")

    passed = []
    failed = []

    # ⚠️ 串行执行：逐个专家依次走完整流程，禁止并行/异步。
    for expert in experts:
        name = expert.get('name', '')
        expert_type = expert.get('type', 'agent')
        if not name:
            continue
        if process_one_expert(name, expert_type, output_dir, session_id):
            passed.append(name)
        else:
            failed.append(name)

    # 汇总
    print(f"\n{'═'*40}")
    print(f"📊 结果: {len(passed)} 成功, {len(failed)} 失败")
    if failed:
        print(f"   失败: {', '.join(failed)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
