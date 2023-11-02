import os
import shutil
import tempfile
from unittest import TestCase
from yappy.callgraph.imports import replace_imports


class TestReplaceImports(TestCase):
    def test_replace_imports(self):
        # Create a temporary module file with some members
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as f:
            f.write("def foo(): pass\n")
            f.write("def bar(): pass\n")
            module_path = f.name
            module_name = os.path.splitext(os.path.basename(module_path))[0]

        # Create a temporary file with a wildcard import from the module
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as f:
            f.write(f"from {module_name} import *\n")
            file_path = f.name

        # Replace the wildcard import with specific imports
        replace_imports(file_path)

        # Check that the import was replaced correctly
        with open(file_path, "r") as f:
            contents = f.read()
            self.assertIn(f"from {module_name} import foo, bar", contents)

        # Clean up temporary files
        os.remove(file_path)
        os.remove(module_path)

    def test_replace_imports_subdir(self):
        # Create a temporary directory with some modules
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module file with some members
            with open(os.path.join(temp_dir, "module1.py"), "w") as f:
                f.write("def func1(): pass\n")
                f.write("def func2(): pass\n")

            # Create a module file with a wildcard import from the first module
            with open(os.path.join(temp_dir, "module2.py"), "w") as f:
                f.write("from module1 import *\n")

            # Create a subdirectory with a module file
            sub_dir = os.path.join(temp_dir, "subdir")
            os.mkdir(sub_dir)
            with open(os.path.join(sub_dir, "module3.py"), "w") as f:
                f.write("def func3(): pass\n")

            # Create a module file with a relative wildcard import from the subdirectory module
            with open(os.path.join(temp_dir, "module4.py"), "w") as f:
                f.write("from .subdir.module3 import *\n")

            # Fix the imports in each module
            replace_imports(os.path.join(temp_dir, "module1.py"))  # noop
            replace_imports(os.path.join(temp_dir, "module2.py"))
            replace_imports(os.path.join(sub_dir, "module3.py"))  # noop
            replace_imports(os.path.join(temp_dir, "module4.py"))

            # Check that the imports were fixed correctly
            with open(os.path.join(temp_dir, "module2.py"), "r") as f:
                contents = f.read()
                self.assertIn("from module1 import func1, func2", contents)

            with open(os.path.join(temp_dir, "module4.py"), "r") as f:
                contents = f.read()
                self.assertIn("from .subdir.module3 import func3", contents)

            # Clean up temporary files
            shutil.rmtree(temp_dir)

    def test_replace_imports_sibling_dir(self):
        # Create a temporary directory with some modules
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module file with some members
            with open(os.path.join(temp_dir, "module1.py"), "w") as f:
                f.write("def func1(): pass\n")
                f.write("def func2(): pass\n")

            # Create a module file with a wildcard import from the first module
            with open(os.path.join(temp_dir, "module2.py"), "w") as f:
                f.write("from module1 import *\n")

            # Create a subdirectory with a module file
            sub_dir = os.path.join(temp_dir, "subdir")
            os.mkdir(sub_dir)
            with open(os.path.join(sub_dir, "module3.py"), "w") as f:
                f.write("def func3(): pass\n")

            # Create a module file with a relative wildcard import from the subdirectory module
            with open(os.path.join(sub_dir, "module4.py"), "w") as f:
                f.write("from ..module1 import *\n")

            # Fix the imports in each module
            replace_imports(os.path.join(temp_dir, "module1.py"))
            replace_imports(os.path.join(temp_dir, "module2.py"))
            replace_imports(os.path.join(sub_dir, "module3.py"))
            replace_imports(os.path.join(sub_dir, "module4.py"))

            # Check that the imports were fixed correctly
            with open(os.path.join(temp_dir, "module2.py"), "r") as f:
                contents = f.read()
                self.assertIn("from module1 import func1, func2", contents)

            with open(os.path.join(sub_dir, "module4.py"), "r") as f:
                contents = f.read()
                self.assertIn("from ..module1 import func1, func2", contents)

            # Clean up temporary files
            shutil.rmtree(temp_dir)
