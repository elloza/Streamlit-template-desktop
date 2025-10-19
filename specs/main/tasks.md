# Tasks: Fix Release Binary - Streamlit Worker Process Crash

**Feature**: Resolve PyInstaller executable failure (exit code 2) on Windows
**Input**: Error logs from v0.1.6 release showing worker process crash
**Root Cause**: Relative path resolution and missing bundled configuration in PyInstaller build

## Context: Release Failure Analysis

The v0.1.6 release executable crashes immediately with exit code 2:

```
[2025-10-18 22:40:02] [ERROR] [root] Streamlit process terminated unexpectedly
[2025-10-18 22:40:02] [ERROR] [root] Process exit code: 2
```

**Root Causes Identified:**
1. CRITICAL: Relative path `src/ui/main_app.py` in worker process cannot be resolved
2. CRITICAL: Missing `.streamlit/config.toml` in PyInstaller bundle
3. HIGH: Missing hidden imports for Streamlit runtime modules
4. HIGH: Working directory mismatch between main and worker processes
5. MEDIUM: Insufficient error capturing from worker process

**Success Criteria:**
- PyInstaller executable launches without crashes
- Streamlit worker process starts successfully within 15 seconds
- Desktop window opens and displays Streamlit UI
- Application works when launched from any directory location

---

## Phase 1: Setup (Diagnostic Infrastructure)

**Purpose**: Add diagnostic tools to capture root cause of future failures

- [X] T001 [P] Add worker process stderr/stdout capture to app.py
- [X] T002 [P] Add PyInstaller freeze detection utility in src/logic/bundle_utils.py
- [X] T003 Create worker subprocess error log file handler in src/logic/logger.py

**Checkpoint**: Can now see actual error messages from worker process crashes ✅ COMPLETE

---

## Phase 2: Foundational (Path Resolution Fix)

**Purpose**: Fix CRITICAL path resolution issues that cause exit code 2

**⚠️ CRITICAL**: These tasks MUST be complete before any user story can work

- [X] T004 Fix relative path issue in _streamlit_worker() by using absolute path in app.py line 40
- [X] T005 [P] Create .streamlit/config.toml with headless server configuration
- [X] T006 [P] Add .streamlit directory to PyInstaller bundle in StreamlitApp.spec datas
- [X] T007 Add bundle root detection function in src/logic/bundle_utils.py
- [X] T008 Update main_app.py to set correct working directory for bundled execution in src/ui/main_app.py lines 10-12
- [X] T009 Add missing Streamlit runtime hidden imports to StreamlitApp.spec line 14

**Checkpoint**: Foundation ready - Streamlit worker can now find and load main_app.py ✅ COMPLETE

---

## Phase 3: User Story 1 - Fix Worker Process Startup (Priority: P1) 🎯 MVP

**Goal**: Streamlit worker process starts successfully and server becomes ready on port 8501

**Independent Test**: Run `dist/StreamlitApp/StreamlitApp.exe` from any directory and verify no crash within 15 seconds

### Implementation for User Story 1

- [ ] T010 [US1] Implement absolute path resolver using bundle_utils.get_bundle_root() in app.py
- [ ] T011 [US1] Replace relative path with absolute path in _streamlit_worker sys.argv in app.py line 40
- [ ] T012 [US1] Add os.chdir() to worker function to ensure correct working directory in app.py
- [ ] T013 [US1] Update wait_for_server timeout from 15 to 30 seconds for slow machines in src/logic/server_manager.py line 39
- [ ] T014 [US1] Add debug logging to show resolved paths before worker spawn in app.py

**Checkpoint**: At this point, worker process should start without FileNotFoundError

---

## Phase 4: User Story 2 - Fix Streamlit Configuration Loading (Priority: P2)

**Goal**: Streamlit loads configuration correctly from bundled .streamlit/config.toml

**Independent Test**: Verify no "config.toml not found" warnings in logs, verify server runs headless

### Implementation for User Story 2

- [ ] T015 [P] [US2] Create .streamlit/config.toml with server.headless=true
- [ ] T016 [P] [US2] Add logger configuration to .streamlit/config.toml
- [ ] T017 [P] [US2] Add client browser settings to .streamlit/config.toml
- [ ] T018 [US2] Update StreamlitApp.spec to bundle .streamlit directory in datas list line 4
- [ ] T019 [US2] Update build_windows.sh to include .streamlit in --add-data flags line 41
- [ ] T020 [US2] Update build_unix.sh to include .streamlit in --add-data flags
- [ ] T021 [US2] Verify config loading in worker by logging config values in src/ui/main_app.py

**Checkpoint**: Streamlit server now runs with correct configuration in bundled executable

---

## Phase 5: User Story 3 - Fix Hidden Imports (Priority: P3)

**Goal**: All Streamlit runtime modules are bundled and worker process can import them

**Independent Test**: No "ModuleNotFoundError" in worker process logs

### Implementation for User Story 3

- [ ] T022 [P] [US3] Add streamlit.runtime.scriptrunner to hidden imports in StreamlitApp.spec
- [ ] T023 [P] [US3] Add streamlit.runtime.app_session to hidden imports in StreamlitApp.spec
- [ ] T024 [P] [US3] Add streamlit.elements.widgets to hidden imports in StreamlitApp.spec
- [ ] T025 [P] [US3] Add streamlit.proto to hidden imports in StreamlitApp.spec
- [ ] T026 [P] [US3] Add streamlit.logger to hidden imports in StreamlitApp.spec
- [ ] T027 [P] [US3] Add pydantic to hidden imports in StreamlitApp.spec
- [ ] T028 [P] [US3] Add typing_extensions to hidden imports in StreamlitApp.spec
- [ ] T029 [P] [US3] Add importlib.metadata to hidden imports in StreamlitApp.spec
- [ ] T030 [US3] Update build_windows.sh with all new hidden imports
- [ ] T031 [US3] Update build_unix.sh with all new hidden imports

**Checkpoint**: All required modules are bundled and importable in worker process

---

## Phase 6: User Story 4 - Improve Error Reporting (Priority: P4)

**Goal**: When worker process fails, capture and log the actual error message

**Independent Test**: Intentionally break worker and verify full traceback appears in logs

### Implementation for User Story 4

- [ ] T032 [US4] Add multiprocessing.Queue for worker errors in app.py
- [ ] T033 [US4] Wrap _streamlit_worker in try/except with error queue in app.py
- [ ] T034 [US4] Read from error queue in main process after worker start in app.py
- [ ] T035 [US4] Log worker stderr to separate file in logs/worker.log
- [ ] T036 [US4] Add worker process health check function in src/logic/server_manager.py
- [ ] T037 [US4] Display worker error in desktop window alert if startup fails in app.py

**Checkpoint**: Developer can see exact Python traceback when worker crashes

---

## Phase 7: User Story 5 - Cross-Platform Path Compatibility (Priority: P5)

**Goal**: Executable works when launched from any directory (desktop, downloads, etc.)

**Independent Test**: Copy .exe to Desktop, run from there, verify it works

### Implementation for User Story 5

- [ ] T038 [P] [US5] Implement Path.resolve() for all file references in app.py
- [ ] T039 [P] [US5] Use Path(__file__).parent for bundle root detection in app.py
- [ ] T040 [US5] Test executable from C:\Users\Desktop location
- [ ] T041 [US5] Test executable from Downloads folder location
- [ ] T042 [US5] Test executable from UNC network path location
- [ ] T043 [US5] Add path normalization for config file loading in src/logic/config_loader.py

**Checkpoint**: Executable works from any launch location on filesystem

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Build verification, documentation, and release readiness

- [X] T044 [P] Update CHANGELOG.md with v0.1.7 fixes
- [X] T045 [P] Update pyproject.toml version to 0.1.7
- [X] T046 Fix .gitignore to not ignore .spec and .streamlit/ directories
- [ ] T047 Run build_windows.sh and verify no build errors
- [ ] T048 Test PyInstaller executable launch from project directory
- [ ] T049 Test PyInstaller executable launch from external directory
- [ ] T050 [P] Add troubleshooting section to README.md for common errors
- [ ] T051 [P] Document .streamlit/config.toml configuration in docs/
- [ ] T052 Commit all changes with descriptive message
- [ ] T053 Create git tag v0.1.7
- [ ] T054 Push tag and trigger GitHub Actions build
- [ ] T055 Verify all three platform builds succeed in CI
- [ ] T056 Create GitHub release with binaries from CI artifacts

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Worker Startup): Can start after Foundational - No dependencies on other stories
  - US2 (Config Loading): Can start after Foundational - Parallel with US1
  - US3 (Hidden Imports): Can start after Foundational - Parallel with US1/US2
  - US4 (Error Reporting): Depends on US1 completion - Needs working subprocess
  - US5 (Path Compatibility): Depends on US1 completion - Needs working paths
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - CRITICAL for release
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent from US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent from US1/US2
- **User Story 4 (P4)**: Depends on US1 (needs working worker process to test error capture)
- **User Story 5 (P5)**: Depends on US1 (needs working paths to test compatibility)

### Within Each User Story

- Diagnostics before implementation
- Path fixes before configuration fixes
- Configuration before imports
- Working process before error reporting
- All core fixes before testing

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- All Foundational tasks marked [P] can run in parallel (T005-T009 after T004)
- US1, US2, US3 can all be implemented in parallel by different developers
- All hidden import additions (T022-T029) can run in parallel
- Path resolution tasks (T038-T039) can run in parallel
- Documentation tasks (T044-T045, T049-T050) can run in parallel

---

## Parallel Example: User Story 3 (Hidden Imports)

```bash
# Launch all hidden import additions together:
Task: "Add streamlit.runtime.scriptrunner to hidden imports"
Task: "Add streamlit.runtime.app_session to hidden imports"
Task: "Add streamlit.elements.widgets to hidden imports"
Task: "Add streamlit.proto to hidden imports"
Task: "Add streamlit.logger to hidden imports"
Task: "Add pydantic to hidden imports"
Task: "Add typing_extensions to hidden imports"
Task: "Add importlib.metadata to hidden imports"
```

---

## Implementation Strategy

### MVP First (User Story 1-3 Only)

1. Complete Phase 1: Setup (diagnostic infrastructure)
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (fix worker startup)
4. Complete Phase 4: User Story 2 (fix config loading)
5. Complete Phase 5: User Story 3 (fix hidden imports)
6. **STOP and VALIDATE**: Build and test executable
7. If working, proceed to Phase 8 (release)

### Incremental Delivery

1. Complete Setup + Foundational → Can diagnose failures
2. Add User Story 1 → Worker starts (may have import errors)
3. Add User Story 2 → Configuration loads correctly
4. Add User Story 3 → All modules import successfully
5. Test executable → **First working release!**
6. Add User Story 4 → Better error messages for future issues
7. Add User Story 5 → Works from any directory
8. Each story adds robustness without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (worker startup)
   - Developer B: User Story 2 (config loading)
   - Developer C: User Story 3 (hidden imports)
3. Integrate all three stories
4. Test combined build
5. Developer A: User Story 4 (error reporting)
6. Developer B: User Story 5 (path compatibility)

---

## Technical Details

### Files to Modify

| File | Changes | Phase |
|------|---------|-------|
| app.py | Absolute paths, error capture, bundle detection | P2, P3, P6 |
| StreamlitApp.spec | Add .streamlit, hidden imports | P2, P5 |
| .streamlit/config.toml | CREATE new file with server config | P4 |
| src/logic/bundle_utils.py | CREATE new file for path resolution | P2 |
| src/ui/main_app.py | Working directory handling | P2 |
| src/logic/server_manager.py | Timeout increase, health check | P3, P6 |
| build/scripts/build_windows.sh | Add .streamlit data, hidden imports | P4, P5 |
| build/scripts/build_unix.sh | Add .streamlit data, hidden imports | P4, P5 |

### Exit Code 2 Analysis

Exit code 2 from the Streamlit worker process indicates:
- `FileNotFoundError`: Most likely cause - can't find src/ui/main_app.py
- `ImportError`: Possible cause - missing hidden imports
- `ConfigError`: Possible cause - missing .streamlit/config.toml

The fix requires addressing all three causes.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each user story or logical group
- Stop at any checkpoint to validate story independently
- Test the executable after each story to catch regressions early
- Avoid: breaking previous working stories, adding features before fixing core issues
