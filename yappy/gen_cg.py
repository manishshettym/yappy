import json
import os

from yappy.callgraph.pycg import CallGraphGenerator, inverse_cg, formats
from yappy.callgraph.imports import fix_repo_imports


repo_path = "./data/dias"
repo_path = fix_repo_imports(repo_path)

python_files = []
for root, dirs, files in os.walk(repo_path):
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.abspath(os.path.join(root, file)))

cg_generator = CallGraphGenerator(python_files, repo_path)
cg_generator.analyze()

formatter = formats.Simple(cg_generator)
cg = formatter.generate()

with open("./results/cg.json", "w+") as f:
    f.write(json.dumps(cg))

with open("./results/icg.json", "w+") as f:
    f.write(json.dumps(inverse_cg(cg)))
