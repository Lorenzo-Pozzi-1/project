import ast
import os
import sys
from collections import defaultdict, deque
from pathlib import Path
import importlib.util
import traceback

class ImportAnalyzer:
    """Analyzes import dependencies to find circular imports and deep recursions."""
    
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.imports = defaultdict(set)  # module -> set of imported modules
        self.reverse_imports = defaultdict(set)  # module -> set of modules that import it
        self.python_files = []
        self.circular_imports = []
        self.deep_chains = []
        
    def find_python_files(self):
        """Find all Python files in the project."""
        for root, dirs, files in os.walk(self.root_path):
            # Skip common build/cache directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'build', 'dist', '.git']]
            
            for file in files:
                if file.endswith('.py'):
                    self.python_files.append(Path(root) / file)
        
        print(f"Found {len(self.python_files)} Python files")
        return self.python_files
    
    def extract_imports(self, file_path):
        """Extract imports from a Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        # Also add submodule imports
                        for alias in node.names:
                            if alias.name != '*':
                                full_import = f"{node.module}.{alias.name}"
                                imports.add(full_import)
            
            return imports
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return set()
    
    def build_import_graph(self):
        """Build the complete import dependency graph."""
        print("Building import graph...")
        
        for file_path in self.python_files:
            # Convert file path to module name
            rel_path = file_path.relative_to(self.root_path)
            if rel_path.name == '__init__.py':
                module_name = str(rel_path.parent).replace(os.sep, '.')
            else:
                module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            # Remove leading dots
            module_name = module_name.lstrip('.')
            
            imports = self.extract_imports(file_path)
            
            # Filter to only local imports (within the project)
            local_imports = set()
            for imp in imports:
                # Check if it's a local import by seeing if it starts with known local modules
                if self.is_local_import(imp):
                    local_imports.add(imp)
            
            self.imports[module_name] = local_imports
            
            # Build reverse import graph
            for imported_module in local_imports:
                self.reverse_imports[imported_module].add(module_name)
    
    def is_local_import(self, import_name):
        """Check if an import is local to the project."""
        # List of known local modules from your project structure
        local_modules = [
            'common', 'data', 'main_page', 'products_page', 
            'eiq_calculator_page', 'season_planner_page', 'help',
            'test_data', 'version_checker', 'main'
        ]
        
        return any(import_name.startswith(module) for module in local_modules)
    
    def find_circular_imports(self):
        """Find circular import dependencies using DFS."""
        print("Searching for circular imports...")
        
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(module):
            if module in rec_stack:
                # Found a cycle
                cycle_start = path.index(module)
                cycle = path[cycle_start:] + [module]
                self.circular_imports.append(cycle)
                return True
            
            if module in visited:
                return False
            
            visited.add(module)
            rec_stack.add(module)
            path.append(module)
            
            for imported_module in self.imports.get(module, set()):
                # Only follow imports that exist in our graph
                if imported_module in self.imports:
                    if dfs(imported_module):
                        return True
            
            rec_stack.remove(module)
            path.pop()
            return False
        
        for module in self.imports:
            if module not in visited:
                dfs(module)
        
        return self.circular_imports
    
    def find_deep_import_chains(self, max_depth=50):
        """Find very deep import chains that could cause recursion."""
        print(f"Searching for import chains deeper than {max_depth}...")
        
        def dfs_depth(module, visited, depth):
            if depth > max_depth:
                return visited.copy()
            
            if module in visited:
                return None  # Circular, but we're looking for deep chains
            
            visited.add(module)
            
            deepest_chain = None
            max_chain_depth = depth
            
            for imported_module in self.imports.get(module, set()):
                if imported_module in self.imports:
                    chain = dfs_depth(imported_module, visited.copy(), depth + 1)
                    if chain and len(chain) > max_chain_depth:
                        deepest_chain = chain
                        max_chain_depth = len(chain)
            
            return deepest_chain
        
        for module in self.imports:
            chain = dfs_depth(module, set(), 0)
            if chain:
                self.deep_chains.append(list(chain))
        
        return self.deep_chains
    
    def analyze_import_complexity(self):
        """Analyze the complexity of the import structure."""
        print("Analyzing import complexity...")
        
        stats = {
            'total_modules': len(self.imports),
            'total_imports': sum(len(imports) for imports in self.imports.values()),
            'most_imported_modules': [],
            'most_importing_modules': [],
            'highly_connected_modules': []
        }
        
        # Find most imported modules
        import_counts = {module: len(importers) 
                        for module, importers in self.reverse_imports.items()}
        most_imported = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats['most_imported_modules'] = most_imported
        
        # Find modules that import the most
        export_counts = {module: len(imports) 
                        for module, imports in self.imports.items()}
        most_importing = sorted(export_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats['most_importing_modules'] = most_importing
        
        # Find highly connected modules (high in + out degree)
        connectivity = {}
        for module in self.imports:
            in_degree = len(self.reverse_imports.get(module, set()))
            out_degree = len(self.imports.get(module, set()))
            connectivity[module] = in_degree + out_degree
        
        highly_connected = sorted(connectivity.items(), key=lambda x: x[1], reverse=True)[:10]
        stats['highly_connected_modules'] = highly_connected
        
        return stats
    
    def generate_report(self):
        """Generate a comprehensive report of potential issues."""
        print("\n" + "="*80)
        print("PYINSTALLER RECURSION DEBUG REPORT")
        print("="*80)
        
        # Basic statistics
        stats = self.analyze_import_complexity()
        print(f"\nBASIC STATISTICS:")
        print(f"Total modules analyzed: {stats['total_modules']}")
        print(f"Total import relationships: {stats['total_imports']}")
        
        # Circular imports
        print(f"\nCIRCULAR IMPORTS FOUND: {len(self.circular_imports)}")
        if self.circular_imports:
            print("⚠️  CRITICAL: These circular imports can cause PyInstaller recursion!")
            for i, cycle in enumerate(self.circular_imports, 1):
                print(f"  {i}. {' → '.join(cycle)}")
        
        # Deep import chains
        print(f"\nDEEP IMPORT CHAINS: {len(self.deep_chains)}")
        if self.deep_chains:
            print("⚠️  WARNING: These deep chains may contribute to recursion:")
            for i, chain in enumerate(self.deep_chains[:5], 1):  # Show top 5
                print(f"  {i}. Chain length {len(chain)}: {' → '.join(list(chain)[:5])}...")
        
        # Most problematic modules
        print(f"\nMOST IMPORTED MODULES (potential bottlenecks):")
        for module, count in stats['most_imported_modules'][:5]:
            print(f"  {module}: imported by {count} modules")
        
        print(f"\nMOST IMPORTING MODULES (potential sources of complexity):")
        for module, count in stats['most_importing_modules'][:5]:
            print(f"  {module}: imports {count} modules")
        
        print(f"\nHIGHLY CONNECTED MODULES (highest risk for recursion):")
        for module, connectivity in stats['highly_connected_modules'][:5]:
            print(f"  {module}: total connections = {connectivity}")
        
        # Recommendations
        print(f"\n🔧 RECOMMENDATIONS:")
        if self.circular_imports:
            print("1. FIX CIRCULAR IMPORTS - This is likely the main cause!")
            print("   - Use lazy imports (import inside functions)")
            print("   - Reorganize code to remove circular dependencies")
            print("   - Use TYPE_CHECKING imports for type hints")
        
        if any(len(chain) > 20 for chain in self.deep_chains):
            print("2. REDUCE IMPORT CHAIN DEPTH")
            print("   - Simplify module structure")
            print("   - Use dependency injection instead of deep imports")
        
        print("3. FOR PYINSTALLER:")
        print("   - Use --hidden-import for problematic modules")
        print("   - Increase recursion limit: sys.setrecursionlimit(5000)")
        print("   - Consider using --exclude-module for unused modules")

def check_pyinstaller_compatibility():
    """Check for common PyInstaller issues."""
    print("\n" + "="*50)
    print("PYINSTALLER COMPATIBILITY CHECK")
    print("="*50)
    
    # Check for problematic imports
    problematic_patterns = [
        'from PySide6.QtWidgets import *',
        'from PySide6.QtCore import *',
        'from PySide6.QtGui import *',
        'from common import *',
    ]
    
    print("Checking for problematic import patterns...")
    issues_found = []
    
    root_path = Path('.')
    for file_path in root_path.rglob('*.py'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in problematic_patterns:
                if pattern in content:
                    issues_found.append((file_path, pattern))
        except Exception:
            continue
    
    if issues_found:
        print("⚠️  Found problematic import patterns:")
        for file_path, pattern in issues_found[:10]:  # Show first 10
            print(f"  {file_path}: {pattern}")
        print("  Recommendation: Use specific imports instead of wildcard imports")
    else:
        print("✅ No problematic import patterns found")

def main():
    """Main debugging function."""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = '.'
    
    print("PyInstaller Recursion Debugger")
    print("=" * 50)
    print(f"Analyzing project at: {os.path.abspath(root_path)}")
    
    # Create analyzer
    analyzer = ImportAnalyzer(root_path)
    
    # Find Python files
    analyzer.find_python_files()
    
    # Build import graph
    analyzer.build_import_graph()
    
    # Find issues
    analyzer.find_circular_imports()
    analyzer.find_deep_import_chains()
    
    # Generate report
    analyzer.generate_report()
    
    # Additional PyInstaller checks
    check_pyinstaller_compatibility()
    
    print(f"\n💡 To run PyInstaller with increased recursion limit:")
    print(f"   python -c \"import sys; sys.setrecursionlimit(5000); import PyInstaller.__main__; PyInstaller.__main__.run()\" your_spec_file.spec")

if __name__ == "__main__":
    main()