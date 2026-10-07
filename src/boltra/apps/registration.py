"""Plan a narrow source edit using AST positions, preserving existing code."""

from __future__ import annotations

import ast
import codecs
import io


def register_router(original: bytes, name: str, attribute: str) -> bytes:
    """Register a router on a direct, top-level FastAPI instance.

    Parse source without importing or executing project code. AST positions locate
    insertion points; the existing source is never regenerated with ``ast.unparse``.
    Factories and nested attributes need a later, explicit registration contract.
    """
    if "." in attribute:
        raise ValueError("add app requires a top-level FastAPI instance (module:app)")
    source = original.decode("utf-8-sig")
    tree = ast.parse(source)
    constructors: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "fastapi":
            constructors.update(
                item.asname or item.name
                for item in node.names
                if item.name == "FastAPI"
            )
        elif isinstance(node, ast.Import):
            constructors.update(
                f"{item.asname or item.name}.FastAPI"
                for item in node.names
                if item.name == "fastapi"
            )

    definitions: list[ast.Assign | ast.AnnAssign] = []
    for node in tree.body:
        assignment: ast.Assign | ast.AnnAssign
        if isinstance(node, ast.Assign):
            assignment = node
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            assignment = node
            targets = [node.target]
        else:
            continue
        if any(
            isinstance(target, ast.Name) and target.id == attribute
            for target in targets
        ):
            definitions.append(assignment)
    if len(definitions) != 1:
        raise ValueError(
            f"expected one top-level '{attribute} = FastAPI(...)' assignment"
        )
    definition = definitions[0]
    value = definition.value
    if not isinstance(value, ast.Call) or ast.unparse(value.func) not in constructors:
        raise ValueError(f"'{attribute}' must be created directly with FastAPI(...)")
    if any(
        node is not definition and node.lineno == definition.end_lineno
        for node in tree.body
    ):
        raise ValueError("put the FastAPI assignment on its own statement line")

    module = f"apps.{name}.router"
    alias = f"_boltra_{name}_router"
    for child in ast.walk(tree):
        if isinstance(child, ast.ImportFrom) and child.module == module:
            raise ValueError(f"router for app '{name}' is already imported")
        if isinstance(child, ast.Name) and child.id == alias:
            raise ValueError(f"registration name '{alias}' is already in use")
        if isinstance(child, ast.alias) and (child.asname or child.name) == alias:
            raise ValueError(f"registration name '{alias}' is already in use")

    # Keep imports before executable code, after a docstring/future imports.
    import_line = 0
    for index, node in enumerate(tree.body):
        docstring = (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        if not docstring and not isinstance(node, ast.Import | ast.ImportFrom):
            break
        import_line = node.end_lineno or node.lineno

    newline = "\r\n" if "\r\n" in source else "\n"
    # Universal source newlines preserve Unicode separators inside string literals.
    lines = io.StringIO(source, newline="").readlines()
    if lines and not lines[-1].endswith(("\n", "\r")):
        lines[-1] += newline
    include_line = definition.end_lineno or definition.lineno
    # Insert from the bottom so earlier AST line offsets remain valid.
    lines.insert(
        include_line,
        f"{newline}# Boltra app: {name}{newline}"
        f"{attribute}.include_router({alias}){newline}",
    )
    lines.insert(import_line, f"from {module} import router as {alias}{newline}")
    updated = "".join(lines)
    ast.parse(updated)  # Refuse an edit that would leave invalid Python source.
    bom = codecs.BOM_UTF8 if original.startswith(codecs.BOM_UTF8) else b""
    return bom + updated.encode("utf-8")
