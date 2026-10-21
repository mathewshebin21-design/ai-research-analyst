"""Reproduces the crash on the main report flow without a browser.

Usage (from any directory):
    python docs/redesign/evidence/apptest_generate_click.py /path/to/ai-research-analyst
"""
import os
import sys

from streamlit.testing.v1 import AppTest

root = os.path.abspath(sys.argv[1])
sys.path.insert(0, root)
os.chdir(root)

at = AppTest.from_file(os.path.join(root, "app.py"), default_timeout=60).run()
print("initial run exceptions:", [e.value for e in at.exception])

button = next(b for b in at.button if "Generate Custom Intelligence Report" in b.label)
at = button.click().run()
print("after Generate click exceptions:")
for e in at.exception:
    print("  ", e.value[:300])
