"""执行受控评估，创建可供 QA 核验的原始产物。"""

import json
import sys

from traceopt.evaluation import run_evaluation


def main():
    if sys.argv[1:] in (["--help"], ["-h"]):
        print("用法：python experiments/evaluate.py 配置JSON 新建输出目录（不覆盖）")
        return 0
    if len(sys.argv) != 3:
        print("错误：需要配置 JSON 和新建输出目录；使用 --help 查看用法。", file=sys.stderr)
        return 2
    try:
        summary = run_evaluation(sys.argv[1], sys.argv[2])
    except (ValueError, OSError) as exc:
        print(f"评估失败：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
