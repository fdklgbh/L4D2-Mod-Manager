# Implementation Plan: Feature-Oriented Source Layout

## Overview

Reorganize the 2.x source tree around feature-owned pages while moving reusable
runtime, configuration, persistence, VPK, and widget code into explicit shared
packages. Preserve the existing `src/main.py` entry point and runtime behavior.

## Decisions

- Pages own their Qt views, generated UI modules, presentation models, dialogs,
  and workers under `features/<feature>/`.
- Shared code must not depend on a feature package.
- This is a structural refactor only. It does not restore unfinished 1.x
  features or migrate user data.

## Tasks

1. [x] Create the target package skeleton and move reusable shared code.
2. [x] Move the application shell and each current page into feature packages.
3. [x] Update imports, Alembic metadata imports, and generated UI imports.
4. [x] Verify imports and lint the moved source files.

## Verification

- Run Ruff against non-generated source files.
- Compile every non-generated Python source file without writing bytecode.
- Confirm the main entry point and Alembic configuration import successfully.
