"""端到端测试：验证数据处理 + 建模完整流程可以运行。"""
import subprocess


def test_cli_entrypoint():
    """验证 main.py 作为脚本可正常执行并退出码为 0"""
    result = subprocess.run(
        ["uv", "run", "python", "main.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"main.py 执行失败: {result.stderr}"
    assert "Hello" in result.stdout


def test_project_importable():
    """验证项目核心依赖均可正常导入"""
    import pandas  # noqa: F401
    import numpy  # noqa: F401
    import sklearn  # noqa: F401
    import matplotlib  # noqa: F401
    import seaborn  # noqa: F401

    # 只要能导入就说明环境没问题
    assert True
