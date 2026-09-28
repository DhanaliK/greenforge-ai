"""
Python AST-based code analyzer for GreenForge AI.
Detects computational inefficiencies through static analysis.
"""
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Issue:
    issue_id: str
    severity: str
    category: str
    title: str
    explanation: str
    evidence: str
    line_start: Optional[int]
    line_end: Optional[int]
    estimated_complexity: Optional[str]
    recommendation: str
    confidence: str
    is_static: bool = True


class PythonAnalyzer:
    """
    Static code analyzer for Python source code.
    Uses AST traversal to detect computational inefficiency patterns.
    """

    def analyze(self, code: str) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(Issue(
                issue_id="SYNTAX_ERROR",
                severity="Critical",
                category="Syntax",
                title="Syntax Error",
                explanation=f"The code contains a syntax error: {e}",
                evidence=str(e),
                line_start=e.lineno,
                line_end=e.lineno,
                estimated_complexity=None,
                recommendation="Fix the syntax error before analysis can proceed.",
                confidence="High",
                is_static=True
            ))
            return issues

        lines = code.splitlines()

        # Run all detection passes
        issues.extend(self._detect_nested_loops(tree, lines))
        issues.extend(self._detect_repeated_calls(tree, lines))
        issues.extend(self._detect_string_concatenation(tree, lines))
        issues.extend(self._detect_list_in_loop(tree, lines))
        issues.extend(self._detect_repeated_indexing(tree, lines))
        issues.extend(self._detect_global_in_loop(tree, lines))
        issues.extend(self._detect_redundant_sorting(tree, lines))
        issues.extend(self._detect_unnecessary_list_conversion(tree, lines))
        issues.extend(self._detect_repeated_file_io(tree, lines))
        issues.extend(self._detect_ml_patterns(tree, lines))
        issues.extend(self._detect_large_data_in_loop(tree, lines))
        return issues

    def _get_source_lines(self, node, lines: List[str]) -> str:
        try:
            start = max(0, node.lineno - 1)
            end = min(len(lines), getattr(node, 'end_lineno', node.lineno))
            return "\n".join(lines[start:end])
        except Exception:
            return ""

    def _detect_nested_loops(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        issues = []

        class LoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_stack = []
                self.found = []

            def _is_loop(self, node):
                return isinstance(node, (ast.For, ast.While))

            def visit_For(self, node):
                self._enter_loop(node)
            def visit_While(self, node):
                self._enter_loop(node)

            def _enter_loop(self, node):
                self.loop_stack.append(node)
                depth = len(self.loop_stack)
                if depth >= 2:
                    outer = self.loop_stack[-2]
                    inner = node
                    self.found.append((depth, outer, inner))
                self.generic_visit(node)
                self.loop_stack.pop()

        visitor = LoopVisitor()
        visitor.visit(tree)

        seen = set()
        for depth, outer, inner in visitor.found:
            key = (outer.lineno, inner.lineno)
            if key in seen:
                continue
            seen.add(key)
            evidence = self._get_source_lines(outer, lines)[:500]
            severity = "Critical" if depth >= 3 else "High"
            issues.append(Issue(
                issue_id=f"NESTED_LOOP_{outer.lineno}",
                severity=severity,
                category="Algorithmic Complexity",
                title=f"Nested Loop (depth {depth}) at line {outer.lineno}",
                explanation=(
                    f"A loop at line {outer.lineno} contains an inner loop at line {inner.lineno}, "
                    f"creating a nesting depth of {depth}. If both loops iterate over input of size n, "
                    "the inner body executes O(n²) or worse times. Whether this is a problem depends "
                    "on expected input sizes and workload characteristics."
                ),
                evidence=evidence,
                line_start=outer.lineno,
                line_end=getattr(inner, 'end_lineno', inner.lineno),
                estimated_complexity=f"O(n^{depth}) heuristic" if depth <= 3 else f"O(n^{depth}+)",
                recommendation=(
                    "Investigate whether the inner loop can be replaced with: "
                    "a hash lookup (O(1)), sorting + two-pointer (O(n log n)), "
                    "set intersection, or vectorized operations (NumPy/Pandas). "
                    "Only refactor if profiling confirms this is a bottleneck."
                ),
                confidence="High",
                is_static=True
            ))
        return issues

    def _detect_repeated_calls(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect repeated function calls inside loops that could be cached."""
        issues = []

        class CallInLoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.loop_node = None
                self.found = []

            def visit_For(self, node):
                old_loop = self.in_loop
                old_node = self.loop_node
                self.in_loop = True
                self.loop_node = node
                self.generic_visit(node)
                self.in_loop = old_loop
                self.loop_node = old_node

            def visit_While(self, node):
                old_loop = self.in_loop
                old_node = self.loop_node
                self.in_loop = True
                self.loop_node = node
                self.generic_visit(node)
                self.in_loop = old_loop
                self.loop_node = old_node

            def visit_Call(self, node):
                if self.in_loop:
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                    expensive = ['len', 'sorted', 'reversed', 'list', 'dict', 'set',
                                 'range', 'open', 'read', 'json', 'load', 'loads',
                                 'compile', 'connect', 'cursor', 'requests']
                    if any(f in func_name.lower() for f in expensive):
                        self.found.append((self.loop_node, node, func_name))
                self.generic_visit(node)

        visitor = CallInLoopVisitor()
        visitor.visit(tree)

        # Deduplicate by function name + loop line
        seen = set()
        for loop_node, call_node, func_name in visitor.found:
            key = (loop_node.lineno, func_name)
            if key in seen:
                continue
            seen.add(key)
            evidence = self._get_source_lines(loop_node, lines)[:400]
            issues.append(Issue(
                issue_id=f"REPEATED_CALL_{loop_node.lineno}_{func_name}",
                severity="Medium",
                category="Repeated Computation",
                title=f"Potentially repeated call to '{func_name}()' inside loop at line {loop_node.lineno}",
                explanation=(
                    f"The function '{func_name}()' is called inside a loop starting at line {loop_node.lineno}. "
                    "If this call returns the same value on each iteration and has no side effects, "
                    "computing it once before the loop may reduce unnecessary work."
                ),
                evidence=evidence,
                line_start=call_node.lineno,
                line_end=call_node.lineno,
                estimated_complexity="Repeated per-iteration cost",
                recommendation=(
                    f"If '{func_name}()' is deterministic and the result does not change during "
                    "the loop, hoist the call outside the loop and reuse the cached value."
                ),
                confidence="Medium",
                is_static=True
            ))
        return issues

    def _detect_string_concatenation(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect string concatenation with += in loops."""
        issues = []

        class AugAssignVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.loop_node = None
                self.found = []

            def visit_For(self, node):
                old = (self.in_loop, self.loop_node)
                self.in_loop = True
                self.loop_node = node
                self.generic_visit(node)
                self.in_loop, self.loop_node = old

            def visit_While(self, node):
                old = (self.in_loop, self.loop_node)
                self.in_loop = True
                self.loop_node = node
                self.generic_visit(node)
                self.in_loop, self.loop_node = old

            def visit_AugAssign(self, node):
                if self.in_loop and isinstance(node.op, ast.Add):
                    self.found.append((self.loop_node, node))
                self.generic_visit(node)

        visitor = AugAssignVisitor()
        visitor.visit(tree)

        seen = set()
        for loop_node, node in visitor.found:
            key = (loop_node.lineno, node.lineno)
            if key in seen:
                continue
            seen.add(key)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"STRING_CONCAT_{node.lineno}",
                severity="Medium",
                category="Inefficient String Operations",
                title=f"Incremental += assignment inside loop at line {node.lineno}",
                explanation=(
                    "Using += to build up a string or list inside a loop may create many intermediate "
                    "objects. For strings, Python strings are immutable; each concatenation allocates a new object. "
                    "For large loops, this can increase memory pressure and execution time."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="O(n²) for string concatenation",
                recommendation=(
                    "For strings: collect substrings in a list and use ''.join(parts) at the end. "
                    "For lists: use list.append() or list comprehension."
                ),
                confidence="Medium",
                is_static=True
            ))
        return issues

    def _detect_list_in_loop(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect 'x in list' membership tests inside loops (O(n) per check)."""
        issues = []

        class InCheckVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.loop_line = None
                self.found = []

            def visit_For(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_While(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_Compare(self, node):
                if self.in_loop:
                    for op in node.ops:
                        if isinstance(op, (ast.In, ast.NotIn)):
                            for comp in node.comparators:
                                # If comparator is a list literal or a name (could be a list)
                                if isinstance(comp, (ast.List, ast.Name)):
                                    self.found.append((self.loop_line, node))
                self.generic_visit(node)

        visitor = InCheckVisitor()
        visitor.visit(tree)

        seen = set()
        for loop_line, node in visitor.found:
            key = (loop_line, node.lineno)
            if key in seen:
                continue
            seen.add(key)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"LIST_MEMBERSHIP_{node.lineno}",
                severity="Medium",
                category="Inefficient Data Structure",
                title=f"List membership test inside loop at line {node.lineno}",
                explanation=(
                    "Checking 'x in list' inside a loop is O(n) per check, making the overall "
                    "complexity O(n²) for n iterations. This is because Python must scan the entire "
                    "list to determine membership."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="O(n²) heuristic",
                recommendation=(
                    "Convert the list to a set before the loop: seen_set = set(my_list). "
                    "Set membership checks are O(1) average, reducing overall complexity to O(n)."
                ),
                confidence="High",
                is_static=True
            ))
        return issues

    def _detect_repeated_indexing(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect repeated dict/list lookups with the same key in a loop."""
        issues = []
        # Simplified: look for the same subscript access appearing > 2 times in a function body
        class FuncVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found = []
            def visit_FunctionDef(self, node):
                counts: Dict[str, List[ast.Subscript]] = {}
                for child in ast.walk(node):
                    if isinstance(child, ast.Subscript):
                        try:
                            key = ast.dump(child)
                            counts.setdefault(key, []).append(child)
                        except Exception:
                            pass
                for key, nodes in counts.items():
                    if len(nodes) >= 3:
                        self.found.append(nodes[0])
                self.generic_visit(node)

        visitor = FuncVisitor()
        visitor.visit(tree)

        seen = set()
        for node in visitor.found:
            if node.lineno in seen:
                continue
            seen.add(node.lineno)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"REPEATED_SUBSCRIPT_{node.lineno}",
                severity="Low",
                category="Repeated Computation",
                title=f"Repeated subscript/indexing expression near line {node.lineno}",
                explanation=(
                    "The same subscript (index/key) access expression appears multiple times "
                    "in the function body. If the container does not change between accesses, "
                    "storing the result in a local variable can improve readability and may "
                    "marginally reduce lookup overhead."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="Minor repeated access",
                recommendation=(
                    "Consider caching the subscript result: value = obj[key] and reuse value."
                ),
                confidence="Low",
                is_static=True
            ))
        return issues

    def _detect_global_in_loop(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect global variable access inside tight loops."""
        return []  # Simplified for now

    def _detect_redundant_sorting(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect sorted() calls inside loops."""
        issues = []

        class SortInLoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.loop_line = None
                self.found = []

            def visit_For(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_Call(self, node):
                if self.in_loop:
                    name = ""
                    if isinstance(node.func, ast.Name):
                        name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        name = node.func.attr
                    if name in ('sorted', 'sort'):
                        self.found.append((self.loop_line, node))
                self.generic_visit(node)

        visitor = SortInLoopVisitor()
        visitor.visit(tree)

        seen = set()
        for loop_line, node in visitor.found:
            key = (loop_line, node.lineno)
            if key in seen:
                continue
            seen.add(key)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"SORT_IN_LOOP_{node.lineno}",
                severity="High",
                category="Algorithmic Complexity",
                title=f"Sorting operation inside loop at line {node.lineno}",
                explanation=(
                    "Calling sorted() or .sort() inside a loop adds O(m log m) work per iteration "
                    "(where m is the size of the sorted collection). If the data being sorted does "
                    "not change between iterations, sorting once before the loop is more efficient."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="O(n * m log m)",
                recommendation=(
                    "If the collection being sorted is constant across iterations, sort it once "
                    "before entering the loop and reuse the sorted result."
                ),
                confidence="High",
                is_static=True
            ))
        return issues

    def _detect_unnecessary_list_conversion(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect list() wrapping of generators that are immediately iterated."""
        issues = []

        class ListWrapVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found = []

            def visit_For(self, node):
                # Check if loop iterates over list(generator)
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'list':
                        self.found.append(node)
                self.generic_visit(node)

        visitor = ListWrapVisitor()
        visitor.visit(tree)

        for node in visitor.found:
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"UNNECESSARY_LIST_{node.lineno}",
                severity="Low",
                category="Unnecessary Memory Allocation",
                title=f"Unnecessary list() wrapping in for-loop at line {node.lineno}",
                explanation=(
                    "Using list() to wrap a generator in a for-loop forces materializing the entire "
                    "collection into memory before iteration begins. Python's for-loop can iterate "
                    "directly over generators, consuming values lazily."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="Unnecessary O(n) allocation",
                recommendation=(
                    "Remove the list() wrapper: 'for x in generator:' is equivalent and avoids "
                    "building the intermediate list."
                ),
                confidence="High",
                is_static=True
            ))
        return issues

    def _detect_repeated_file_io(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect file open() or read() calls inside loops."""
        issues = []

        class FileInLoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.loop_line = None
                self.found = []

            def visit_For(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_While(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_Call(self, node):
                if self.in_loop:
                    name = ""
                    if isinstance(node.func, ast.Name):
                        name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        name = node.func.attr
                    if name in ('open', 'read', 'readlines', 'write'):
                        self.found.append((self.loop_line, node, name))
                self.generic_visit(node)

        visitor = FileInLoopVisitor()
        visitor.visit(tree)

        seen = set()
        for loop_line, node, name in visitor.found:
            key = (loop_line, name)
            if key in seen:
                continue
            seen.add(key)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"FILE_IO_LOOP_{node.lineno}",
                severity="High",
                category="Repeated I/O",
                title=f"File I/O call '{name}()' inside loop at line {node.lineno}",
                explanation=(
                    f"The file operation '{name}()' is called inside a loop. Repeated file I/O "
                    "operations per iteration can be significantly slower than reading/writing in bulk, "
                    "as each call involves OS-level system call overhead."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="O(n) I/O operations",
                recommendation=(
                    "Batch I/O operations. For reading: read the file once before the loop. "
                    "For writing: collect output and write in one call, or use a buffered writer."
                ),
                confidence="High",
                is_static=True
            ))
        return issues

    def _detect_ml_patterns(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect common ML inefficiency patterns."""
        issues = []

        class MLPatternVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found = []
                self.in_loop = False
                self.loop_line = None

            def visit_For(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_Call(self, node):
                name = ""
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr

                # Model loading in loop
                if self.in_loop and name in ('load_model', 'from_pretrained', 'load', 'joblib'):
                    if hasattr(node.func, 'attr') and node.func.attr in ('load', 'from_pretrained'):
                        self.found.append(('model_load_in_loop', self.loop_line, node))

                # Non-batched inference
                if self.in_loop and name in ('predict', 'forward', 'infer', 'run'):
                    self.found.append(('inference_in_loop', self.loop_line, node))

                self.generic_visit(node)

        visitor = MLPatternVisitor()
        visitor.visit(tree)

        seen = set()
        for kind, loop_line, node in visitor.found:
            key = (kind, loop_line)
            if key in seen:
                continue
            seen.add(key)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""

            if kind == 'model_load_in_loop':
                issues.append(Issue(
                    issue_id=f"ML_MODEL_LOAD_LOOP_{node.lineno}",
                    severity="Critical",
                    category="ML Efficiency",
                    title=f"Model loading inside loop at line {node.lineno}",
                    explanation=(
                        "Loading a model inside a loop causes repeated disk I/O and model "
                        "initialization overhead per iteration. Model loading is typically "
                        "one of the most expensive operations in an ML pipeline."
                    ),
                    evidence=evidence,
                    line_start=node.lineno,
                    line_end=node.lineno,
                    estimated_complexity="O(n) expensive model loads",
                    recommendation=(
                        "Load the model once before the loop and reuse the model object "
                        "for all inference calls."
                    ),
                    confidence="High",
                    is_static=True
                ))
            elif kind == 'inference_in_loop':
                issues.append(Issue(
                    issue_id=f"ML_INFERENCE_LOOP_{node.lineno}",
                    severity="High",
                    category="ML Efficiency",
                    title=f"Single-sample inference inside loop at line {node.lineno}",
                    explanation=(
                        "Calling predict/infer on individual samples in a loop prevents "
                        "hardware from leveraging batched matrix operations. Batching "
                        "allows efficient utilization of SIMD/GPU parallelism."
                    ),
                    evidence=evidence,
                    line_start=node.lineno,
                    line_end=node.lineno,
                    estimated_complexity="n individual inference calls vs. 1 batched call",
                    recommendation=(
                        "Collect inputs into a batch and call predict(batch) once, "
                        "rather than predict(item) n times."
                    ),
                    confidence="Medium",
                    is_static=True
                ))
        return issues

    def _detect_large_data_in_loop(self, tree: ast.AST, lines: List[str]) -> List[Issue]:
        """Detect copy.deepcopy or large constructor calls inside loops."""
        issues = []

        class DeepCopyVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.loop_line = None
                self.found = []

            def visit_For(self, node):
                old = (self.in_loop, self.loop_line)
                self.in_loop = True
                self.loop_line = node.lineno
                self.generic_visit(node)
                self.in_loop, self.loop_line = old

            def visit_Call(self, node):
                if self.in_loop:
                    name = ""
                    if isinstance(node.func, ast.Name):
                        name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        name = node.func.attr
                    if name in ('deepcopy', 'copy'):
                        self.found.append((self.loop_line, node, name))
                self.generic_visit(node)

        visitor = DeepCopyVisitor()
        visitor.visit(tree)

        seen = set()
        for loop_line, node, name in visitor.found:
            key = (loop_line, node.lineno)
            if key in seen:
                continue
            seen.add(key)
            evidence = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            issues.append(Issue(
                issue_id=f"COPY_IN_LOOP_{node.lineno}",
                severity="Medium",
                category="Excessive Memory Allocation",
                title=f"Object copying ({name}) inside loop at line {node.lineno}",
                explanation=(
                    f"Calling {name}() inside a loop creates new object copies per iteration, "
                    "increasing memory allocation pressure and GC overhead."
                ),
                evidence=evidence,
                line_start=node.lineno,
                line_end=node.lineno,
                estimated_complexity="O(n) copies",
                recommendation=(
                    "Consider whether copying is necessary each iteration. If the original "
                    "object is not mutated, sharing a reference avoids unnecessary allocation."
                ),
                confidence="High",
                is_static=True
            ))
        return issues


class JavaScriptAnalyzer:
    """Text/pattern-based JavaScript/TypeScript analyzer."""

    def analyze(self, code: str) -> List[Issue]:
        issues = []
        lines = code.splitlines()

        # Detect nested for loops
        loop_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if re.match(r'^for\s*\(', stripped) or re.match(r'^while\s*\(', stripped):
                loop_lines.append(i)

        # Simple nesting detection based on indentation
        for j, line_num in enumerate(loop_lines):
            for k in range(j + 1, len(loop_lines)):
                if loop_lines[k] - line_num < 20:
                    issues.append(Issue(
                        issue_id=f"JS_NESTED_LOOP_{line_num}",
                        severity="High",
                        category="Algorithmic Complexity",
                        title=f"Potential nested loop near line {line_num}",
                        explanation="Multiple loop constructs detected in close proximity, suggesting potential O(n²) pattern.",
                        evidence="\n".join(lines[line_num - 1:line_num + 3]),
                        line_start=line_num,
                        line_end=loop_lines[k],
                        estimated_complexity="O(n²) heuristic",
                        recommendation="Investigate whether the inner loop can be replaced with a Map/Set lookup.",
                        confidence="Low",
                        is_static=True
                    ))
                    break

        # Detect array.indexOf/includes in loops
        for i, line in enumerate(lines, 1):
            if re.search(r'\.indexOf\(|\.includes\(', line):
                issues.append(Issue(
                    issue_id=f"JS_ARRAY_SEARCH_{i}",
                    severity="Medium",
                    category="Inefficient Data Structure",
                    title=f"Array search operation at line {i}",
                    explanation="Array indexOf/includes is O(n). If used inside a loop, overall complexity becomes O(n²).",
                    evidence=lines[i - 1],
                    line_start=i,
                    line_end=i,
                    estimated_complexity="O(n) per call",
                    recommendation="Use a Set or Map for O(1) membership tests.",
                    confidence="Medium",
                    is_static=True
                ))

        return issues


def get_analyzer(language: str):
    lang = language.lower().strip()
    if lang in ("python", "py"):
        return PythonAnalyzer()
    elif lang in ("javascript", "js", "typescript", "ts"):
        return JavaScriptAnalyzer()
    else:
        return PythonAnalyzer()  # default to Python
