# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

hiddenimports = (
    collect_submodules("uvicorn")
    + collect_submodules("fastapi")
    + collect_submodules("pydantic")
    + collect_submodules("solver")
    + [
        "main",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "uvicorn.importer",
        "uvicorn.config",
        "uvicorn.server",
        "uvicorn.main",
        "uvicorn.workers",
        "uvicorn.middleware",
        "uvicorn.middleware.proxy_headers",
        "uvicorn.middleware.wsgi",
        "uvicorn.middleware.message_logger",
        "uvicorn.middleware.asgi2",
        "uvicorn.supervisors",
        "uvicorn.supervisors.basereload",
        "uvicorn.supervisors.multiprocess",
        "uvicorn.supervisors.statreload",
        "uvicorn.supervisors.watchfilesreload",
        "uvicorn._subprocess",
        "h11",
        "anyio",
        "anyio._backends",
        "anyio._backends._asyncio",
        "starlette",
        "starlette.routing",
        "starlette.middleware",
        "starlette.middleware.cors",
        "starlette.responses",
        "email_validator",
        "annotated_types",
        "pydantic_core",
        "pydantic.deprecated.decorator",
        "pydantic._internal._config",
        "pydantic._internal._generate_schema",
        "pydantic._internal._model_construction",
    ]
)

a = Analysis(
    ["run_server.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["ortools"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="d2-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="d2-backend",
)
