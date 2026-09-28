"""
Complexity analyzer for GreenForge AI.
Provides cyclomatic complexity, loop depth, and Big-O heuristics.
"""
import ast
from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class ComplexityResult:
    function_name: str
    estimated_complexity: str
    confidence: str
    reason: str
    cyclomatic_complexity: Optional[int]
    line_start: Optional[int]
    line_end: Optional[int]
    loop_depth: int = 0


class ComplexityAnalyzer:

    def analyze(self, code: str) -> Dict:
        """
        Analyze Python code for complexity metrics.
        Returns a dict matching ComplexityReport schema.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {
                "total_functions": 0,
                "total_classes": 0,
                "max_loop_depth": 0,
                "findings": [],
                "summary": "Could not analyze code due to syntax error."
            }

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        max_loop_depth = self._max_loop_depth(tree)
        findings = []

        for func in functions:
            result = self._analyze_function(func)
            findings.append({
                "function_name": result.function_name,
                "estimated_complexity": result.estimated_complexity,
                "confidence": result.confidence,
                "reason": result.reason,
                "cyclomatic_complexity": result.cyclomatic_complexity,
                "line_start": result.line_start,
            })

        summary_parts = [f"{len(functions)} function(s), {len(classes)} class(es), max loop depth {max_loop_depth}."]
        if any(f["estimated_complexity"] in ("O(n²)", "O(n³)", "O(n^3)") for f in findings):
            summary_parts.append("Potential polynomial complexity detected.")

        return {
            "total_functions": len(functions),
            "total_classes": len(classes),
            "max_loop_depth": max_loop_depth,
            "findings": findings,
            "summary": " ".join(summary_parts)
        }

    def _analyze_function(self, func: ast.FunctionDef) -> ComplexityResult:
        loop_depth = self._max_loop_depth(func)
        cyclomatic = self._cyclomatic_complexity(func)

        if loop_depth >= 3:
            complexity = "O(n³) heuristic"
            confidence = "Medium"
            reason = f"Three or more nested loops detected (depth={loop_depth}). Complexity grows cubically with input size."
        elif loop_depth == 2:
            complexity = "O(n²) heuristic"
            confidence = "Medium"
            reason = f"Two nested loops detected. Inner body executes approximately n² times for input of size n."
        elif loop_depth == 1:
            complexity = "O(n) heuristic"
            confidence = "Medium"
            reason = "Single loop detected. Iterates linearly over input."
        elif cyclomatic and cyclomatic > 10:
            complexity = "High cyclomatic complexity"
            confidence = "Medium"
            reason = f"Cyclomatic complexity of {cyclomatic} suggests complex branching logic."
        else:
            complexity = "O(1) or unknown"
            confidence = "Low"
            reason = "No loops or high branching detected at this analysis depth."

        return ComplexityResult(
            function_name=func.name,
            estimated_complexity=complexity,
            confidence=confidence,
            reason=reason,
            cyclomatic_complexity=cyclomatic,
            line_start=func.lineno,
            line_end=getattr(func, 'end_lineno', None),
            loop_depth=loop_depth
        )

    def _max_loop_depth(self, node: ast.AST, current: int = 0) -> int:
        """Recursively compute max loop nesting depth."""
        max_depth = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                depth = self._max_loop_depth(child, current + 1)
            else:
                depth = self._max_loop_depth(child, current)
            if depth > max_depth:
                max_depth = depth
        return max_depth

    def _cyclomatic_complexity(self, func: ast.AST) -> int:
        """
        Simplified cyclomatic complexity: count decision points + 1.
        Decision points: if, elif, for, while, except, with, assert, comprehension conditions.
        """
        decision_nodes = (ast.If, ast.For, ast.While, ast.ExceptHandler,
                          ast.With, ast.Assert, ast.comprehension)
        count = 1
        for node in ast.walk(func):
            if isinstance(node, decision_nodes):
                count += 1
            elif isinstance(node, ast.BoolOp):
                count += len(node.values) - 1
        return count
