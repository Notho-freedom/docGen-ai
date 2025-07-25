"""
Documentation generator for Python files using AST parsing.

Extracts classes, functions, docstrings and generates JSON documentation.
"""

import ast
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import click

from .utils import (
    get_git_repo, 
    get_commit_info, 
    load_docignore, 
    get_python_files,
    ensure_directory
)


class PythonDocumentationExtractor:
    """Extract documentation from Python files using AST."""
    
    def __init__(self):
        self.current_file = None
    
    def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract documentation from a single Python file."""
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=file_path)
            
            doc_data = {
                "path": file_path,
                "module_docstring": ast.get_docstring(tree),
                "imports": self._extract_imports(tree),
                "classes": self._extract_classes(tree),
                "functions": self._extract_functions(tree),
                "constants": self._extract_constants(tree),
                "generated_at": datetime.now().isoformat()
            }
            
            return doc_data
            
        except Exception as e:
            click.echo(f"⚠️  Warning: Could not parse {file_path}: {e}")
            return {
                "path": file_path,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Extract import statements."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": node.module or "",
                        "name": alias.name,
                        "alias": alias.asname
                    })
        
        return imports
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "line_number": node.lineno,
                    "bases": [self._get_name(base) for base in node.bases],
                    "decorators": [self._get_name(dec) for dec in node.decorator_list],
                    "methods": self._extract_methods(node),
                    "properties": self._extract_properties(node)
                }
                classes.append(class_info)
        
        return classes
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract top-level function definitions."""
        functions = []
        
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_info = self._extract_function_info(node)
                functions.append(func_info)
        
        return functions
    
    def _extract_methods(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract methods from a class."""
        methods = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_info = self._extract_function_info(node, is_method=True)
                methods.append(method_info)
        
        return methods
    
    def _extract_properties(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract properties from a class."""
        properties = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                # Check if it's a property
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Name) and decorator.id == 'property') or \
                       (isinstance(decorator, ast.Attribute) and decorator.attr == 'property'):
                        prop_info = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "line_number": node.lineno,
                            "type": "property"
                        }
                        properties.append(prop_info)
                        break
        
        return properties
    
    def _extract_function_info(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """Extract information from a function or method."""
        args_info = self._extract_arguments(node.args)
        
        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "line_number": node.lineno,
            "arguments": args_info,
            "decorators": [self._get_name(dec) for dec in node.decorator_list],
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "is_method": is_method,
            "returns": self._get_return_annotation(node)
        }
        
        if is_method:
            func_info["is_classmethod"] = any(
                self._get_name(dec) == "classmethod" for dec in node.decorator_list
            )
            func_info["is_staticmethod"] = any(
                self._get_name(dec) == "staticmethod" for dec in node.decorator_list
            )
            func_info["is_private"] = node.name.startswith("_")
        
        return func_info
    
    def _extract_arguments(self, args: ast.arguments) -> List[Dict[str, Any]]:
        """Extract function arguments information."""
        arguments = []
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            arg_info = {
                "name": arg.arg,
                "type": self._get_annotation(arg.annotation),
                "has_default": i >= len(args.args) - len(args.defaults),
                "default": None
            }
            
            if arg_info["has_default"]:
                default_idx = i - (len(args.args) - len(args.defaults))
                if default_idx >= 0:
                    arg_info["default"] = self._get_default_value(args.defaults[default_idx])
            
            arguments.append(arg_info)
        
        # *args
        if args.vararg:
            arguments.append({
                "name": f"*{args.vararg.arg}",
                "type": self._get_annotation(args.vararg.annotation),
                "is_vararg": True
            })
        
        # **kwargs
        if args.kwarg:
            arguments.append({
                "name": f"**{args.kwarg.arg}",
                "type": self._get_annotation(args.kwarg.annotation),
                "is_kwarg": True
            })
        
        return arguments
    
    def _extract_constants(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract module-level constants."""
        constants = []
        
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        const_info = {
                            "name": target.id,
                            "line_number": node.lineno,
                            "value": self._get_value_repr(node.value)
                        }
                        constants.append(const_info)
        
        return constants
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ast.dump(node)
    
    def _get_annotation(self, annotation: Optional[ast.AST]) -> Optional[str]:
        """Get type annotation as string."""
        if annotation is None:
            return None
        return self._get_name(annotation)
    
    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation."""
        if node.returns:
            return self._get_name(node.returns)
        return None
    
    def _get_default_value(self, node: ast.AST) -> str:
        """Get default value representation."""
        return self._get_value_repr(node)
    
    def _get_value_repr(self, node: ast.AST) -> str:
        """Get string representation of a value node."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            return "[...]"
        elif isinstance(node, ast.Dict):
            return "{...}"
        else:
            return ast.dump(node)


def generate_documentation(commit_hash: Optional[str] = None) -> bool:
    """
    Generate documentation for the current or specified commit.
    
    Args:
        commit_hash: Optional commit hash to generate docs for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Git repository
        repo = get_git_repo()
        if not repo:
            click.echo("❌ Error: Not in a Git repository.")
            return False
        
        # Get commit information
        commit_info = get_commit_info(repo, commit_hash)
        if not commit_info:
            return False
        
        click.echo(f"📝 Generating documentation for commit {commit_info['short_hash']}...")
        
        # Load .docignore patterns
        docignore_spec = load_docignore()
        
        # Get Python files to document
        python_files = get_python_files(docignore_spec=docignore_spec)
        
        if not python_files:
            click.echo("⚠️  No Python files found to document.")
            return True
        
        # Initialize extractor
        extractor = PythonDocumentationExtractor()
        
        # Ensure .docshadow directory exists
        ensure_directory(".docshadow")
        
        # Generate documentation for each file
        documented_files = []
        for py_file in python_files:
            click.echo(f"  📄 Processing {py_file}...")
            
            # Extract documentation
            doc_data = extractor.extract_from_file(py_file)
            
            # Create output path (mirror source structure)
            output_path = Path(".docshadow") / f"{py_file}.json"
            ensure_directory(output_path.parent)
            
            # Write documentation JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(doc_data, f, indent=2, ensure_ascii=False)
            
            documented_files.append(f"{py_file}.json")
        
        # Generate index.json
        index_data = {
            "commit": commit_info['hash'],
            "short_commit": commit_info['short_hash'],
            "date": commit_info['date'],
            "message": commit_info['message'],
            "author": commit_info['author'],
            "files": documented_files
        }
        
        with open(".docshadow/index.json", 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        # Generate docshadow.json (project structure mapping)
        project_structure = _build_project_structure(python_files)
        docshadow_data = {
            "project": Path.cwd().name,
            "generated_at": datetime.now().isoformat(),
            "commit": commit_info['hash'],
            "structure": project_structure
        }
        
        with open(".docshadow/docshadow.json", 'w', encoding='utf-8') as f:
            json.dump(docshadow_data, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✅ Documentation generated successfully!")
        click.echo(f"   📁 {len(documented_files)} files documented")
        click.echo(f"   📋 Index: .docshadow/index.json")
        click.echo(f"   🗺️  Structure: .docshadow/docshadow.json")
        
        return True
        
    except Exception as e:
        click.echo(f"❌ Error generating documentation: {e}", err=True)
        return False


def _build_project_structure(python_files: List[str]) -> Dict[str, Any]:
    """Build nested project structure for docshadow.json."""
    structure = {}
    
    for py_file in python_files:
        parts = Path(py_file).parts
        current = structure
        
        # Navigate/create nested structure
        for part in parts[:-1]:  # All parts except filename
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add file mapping
        filename = parts[-1]
        current[filename] = f"{py_file}.json"
    
    return structure 