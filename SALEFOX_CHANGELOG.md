# SALEFOX CHANGELOG

All notable changes to the SaleFox multi-store price comparison and automation engine are documented in this file.
The project adheres to Semantic Versioning (`MAJOR.MINOR.PATCH`).

---

## [1.0.0-rc1] - 2026-11-12

### Security & Hardening (P0)
- **Git Secret & Profile Protection (SR-02)**:
  - Overhauled `.gitignore` to strictly exclude all environment files (`.env`, `.env.*`, while whitelisting `!.env.example`).
  - Added exclusion rules for browser session state, automation cookies, and runtime profiles: `**/amazon_profiles/`, `**/reliance_profiles/`, `**/user-data/`, `**/browser_profiles/`.
  - Added exclusion for Python virtual environments (`.venv/`, `env/`), build outputs (`dist/`), and bytecode caches (`__pycache__/`).
  - Validated rules using `git check-ignore -v` to ensure zero secrets or profiles can enter source control.
- **Fail-Closed Checkout Automation Safety (SR-03)**:
  - In `src/backend/unified_automation.py`, eliminated dangerous default customer profiles containing placeholder phones (`9876543210`), dummy names (`SaleFox Customer`), and hardcoded Dehradun addresses.
  - Implemented `validate_checkout_request()` with rigorous validation checks: enforces minimum field lengths, 10-digit Indian mobile validation, 6-digit postal PIN code format, real email syntax, and blacklists known placeholders.
  - Added three explicit automation modes: `inspection` (read-only product inspection), `dry_run` (default; fills form but does not place order), and `production` (strictly requires `user_confirmed: true`).
  - Added safe purchase hold in `click_place_order()` to prevent automated financial debiting.
  - Removed developer-specific DOM query `//span[contains(., 'DEBRAJ')]` from Croma shipping module; replaced with generic address radio button selector. Removed `"debraj"` hardcoding from Flipkart verification.
  - Updated Flask & FastAPI `/api/automation/start` endpoints to reject unconfigured/dummy profiles with HTTP 400 (`code: "CHECKOUT_SAFETY_VIOLATION"`).

### Reliability & Portability (P1)
- **Frontend Startup Script Portability (SR-01)**:
  - Updated `start_frontend.bat` with directory-anchoring command `cd /d "%~dp0"`, allowing execution from any directory or shortcut without path errors.
  - Converted unsafe `::` comments inside block structures to standard `REM` commands.
  - Escaped parentheses inside echo messages to prevent Windows Command Processor parsing exceptions.
  - Added pre-flight check for `node_modules` with actionable troubleshooting messages.
- **Data Provenance & Freshness Indicators (SR-04)**:
  - In `src/services/searchService.js`, enhanced `transformUniversalScrapedItem()` to calculate honest data provenance: `dataSource`, `dataMode` (`live_api`, `live_fulfillment`, `live_scraper`, `cached_fallback`, `cached_catalog`), `isLive`, `isFallback`, and `freshnessLabel`.
  - Updated bundled disk catalog items loaded via `getInitialAllProducts()` to honestly display `isLive: false` with label `"Store Catalog"`.
  - In `src/components/ProductCard.jsx`, added a prominent `.product-freshness-pill` with green dot indicator for live scrapes (`● Live Store API`) vs gray ring indicator for static data (`○ Store Catalog`).
  - Added CSS styling in `src/App.css` for freshness pills, including pulse animations and high-contrast badges.

### Performance & Optimization (P2)
- **High-Performance Lightweight Health Check (SR-05)**:
  - Implemented dedicated `@app.route("/api/health")` and `/health` endpoints across all 9 backend microservices (Amazon, Flipkart, Vivo, Samsung, Croma, Apple, Reliance Digital, Oppo, JioMart).
  - Health check responses are under 115 bytes (Amazon dropped from 1,201,030 bytes to 60 bytes — 99.995% payload reduction) and respond in <20ms.
  - Updated `src/services/searchService.js` and `run_all_backends.py` to prioritize `/api/health` before falling back to `/api/status`.
  - In Amazon `web_server.py`, optimized `/api/status` to omit 510-item catalogs when queries are active or when `light=1` query parameter is supplied.
  - In Vivo `web_server.py`, prevented full catalog transmissions during active scrape operations.
- **Catalog Count Reconciliation (SR-06)**:
  - Created automated diagnostic tool `scratch/reconcile_catalogs.py` to reconcile product counts.
  - Verified exact mathematical composition: 1,320 in-memory items across 9 active backends (Amazon: 510, Samsung: 488, JioMart: 186, Apple: 58, Oppo: 54, Vivo: 13, Reliance: 5, Croma: 4, Flipkart: 2).
  - Reconciled bundled frontend catalog: 705 raw entries yielding 684 unique product models and 21 cross-store overlapping models.
- **Linter Standardization & React Bug Remediation (SR-07)**:
  - Configured `.oxlintrc.json` with browser and ES2022 environments, global browser symbols, and 105 active rules targeting `src/**`.
  - Discovered and fixed runtime bugs in `src/App.jsx`:
    - Fixed `ReferenceError: isBackendOnline is not defined` on line 1079 by deriving state from `scraperStatuses`.
    - Fixed `ReferenceError: scraperProgress is not defined` on lines 746-754 by introducing dedicated React state hook and wiring it into search callbacks.
  - Cleaned up unused imports in `ProductCard.jsx` and `SamsungBulkBotModal.jsx`.
  - `npm run lint` now executes cleanly with 0 errors across all 13 source files.

### Store Architecture & Governance (P3)
- **Unimplemented Store Status Integrity (SR-08)**:
  - Confirmed that Vijay Sales, Poorvika, Sangeetha, OnePlus, and Xiaomi have no backend implementations.
  - Verified frontend configuration in `src/services/scrapersConfig.js` marks all 5 as `isActive: false` and `status: "Coming Soon"`.
  - Confirmed UI prevents user activation and network requests are never dispatched to unallocated ports.
- **Legacy Directory Preservation & Audit (SR-09)**:
  - Executed automated codebase audit via `scratch/audit_legacy_dirs.py` for `Amazon-Scraper-main/`, `Amazon-Scraper-Node/`, `Apple/`, and `Vivo/`.
  - Confirmed these directories are standalone historical reference prototypes not imported by the main application.
  - Preserved existing files in place to protect institutional engineering history while ensuring zero build or runtime impact.

### Master Verification & Test Evidence (SR-10)
- **Automated Regression Suite (`scratch/full_system_regression.py`)**:
  - Validated concurrent startup of all 9 backend microservices within 2.6 seconds.
  - Verified health check payload sizes and response latencies across all 9 ports.
  - Verified fail-closed checkout safety APIs rejecting invalid/placeholder data and accepting valid dry-run profiles.
  - Verified cross-store search execution and item parsing across 8 retailers.
  - Verified clean process termination and complete port release with zero zombie processes.
- **Comprehensive Test Evidence Collection**:
  - Stored all execution outputs and JSON reports in `SALEFOX_TEST_EVIDENCE/`:
    - `catalog_reconciliation_report.json`
    - `checkout_safety_unit_test.txt`
    - `frontend_batch_portability_test.txt`
    - `frontend_build_output.txt`
    - `git_security_check.txt`
    - `legacy_directories_audit.json`
    - `lint_check_output.txt`
    - `master_regression_output.txt`
    - `master_regression_results.json`

---

## [0.9.0-stabilized] - 2026-11-12
- Created root `requirements.txt` unifying dependencies across all 9 scraper microservices.
- Automated Python virtual environment (`.venv`) detection in `start_backends.bat` and `run_all_backends.py`.
- Replaced machine-specific hardcoded paths with portable relative paths and environment variable overrides.
- Resolved port collisions between Oppo (5057) and Vijay Sales (formerly 5057).

