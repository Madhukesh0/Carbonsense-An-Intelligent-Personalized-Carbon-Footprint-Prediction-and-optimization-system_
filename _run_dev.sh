#!/usr/bin/env bash
cd /d/proj
rm -f dev-server.log .run.pid
export NODE_ENV=development
export PYTHON_EXECUTABLE="C:/Users/Admin/AppData/Local/Programs/Python/Python312/python.exe"
export FASTAPI_INTERNAL_PORT=8015
exec pnpm exec tsx watch server/_core/index.ts