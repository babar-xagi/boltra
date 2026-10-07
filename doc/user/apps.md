# Modular FastAPI apps

An app groups related API routes in a Python package. Phase 5 implements app
creation and explicit router registration; generated code uses ordinary FastAPI
and does not import Boltra at runtime.

## Create an app

From a generated project or any of its subdirectories:

```bash
boltra add app students
boltra dev
```

The command creates:

```text
school_api/
├── main.py                 # Existing FastAPI app, with router registration
├── settings.py             # Existing settings
└── apps/
    ├── __init__.py          # Shared apps package; existing contents are preserved
    └── students/
        ├── __init__.py      # Students package
        └── router.py        # APIRouter and a working starter endpoint
```

Open `http://127.0.0.1:8000/students/` using the configured server host/port. The
response is:

```json
{"app": "students", "status": "ok"}
```

The endpoint also appears under the `students` tag in `/docs`. If `boltra dev`
is already running, changing the application source triggers its usual reload.

## Extend the router

`apps/students/router.py` contains:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/")
async def home() -> dict[str, str]:
    return {"app": "students", "status": "ok"}
```

Add your routes directly to this router:

```python
@router.get("/{student_id}")
async def get_student(student_id: int) -> dict[str, int]:
    return {"student_id": student_id}
```

Visit `/students/42` to receive `{"student_id": 42}`. Add schemas, services, and
other files inside the app package when your application needs them; no ORM,
authentication, or database tables are created by this command.

## Registration behavior

Boltra reads `[tool.boltra].app`, finds that module's `.py` file relative to the
project root, and inserts a router import and an `include_router()` call. For
`main:app`, the inserted code is equivalent to:

```python
from apps.students.router import router as _boltra_students_router

# After the existing app = FastAPI(...) construction:
app.include_router(_boltra_students_router)
```

Registration happens before later top-level code, including a main guard. Existing
source is preserved; AST parsing locates insertion points without executing the
project. Comments, a UTF-8 BOM, and LF/CRLF line endings are retained.

`backend.main:application` also works when `backend/main.py` directly creates
`application = FastAPI(...)`. Annotated assignments and imported FastAPI aliases
are supported. Factories, imported/reassigned app objects, nested attributes such
as `container.app`, and targets resolving only to a package's `__init__.py` are
outside this first app scaffolding contract. Unsupported source produces an error before files are
created. The development server's existing target support remains broader.

## Names, conflicts, and recovery

Use a lowercase ASCII Python package name starting with a letter, for example
`students`, `student_records`, or `courses2`. Keywords, soft keywords, Windows
device names, hyphens, uppercase letters, and path separators are rejected.

An existing app is never overwritten. Conflicting `apps.py`, linked paths,
existing router imports, and occupied registration aliases also produce errors.
If writing fails, Boltra removes only the files/directories it created. Existing
package contents and the application source are preserved. Source replacement is
atomic; an editor change detected before replacement cancels the operation.

Phase 5 does not change `INSTALLED_APPS`, install dependencies, or scan directories
at runtime. Registration is explicit source code. Safe `remove app`, structured
settings updates, and router auto-discovery are later phases. Until removal is
implemented, remove an app's import and `include_router()` call before deleting
its package.

See the [CLI reference](cli.md), [settings reference](settings.md), and
[roadmap](../plan/phase.md).

For FastAPI's native router model, see its official
[multiple-file applications guide](https://fastapi.tiangolo.com/tutorial/bigger-applications/).
