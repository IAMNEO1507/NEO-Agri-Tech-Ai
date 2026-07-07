#!/usr/bin/env python3
"""
AgriTech Project Migration Script
==================================
Restructures the project into organized folders and rewrites all internal paths.
Usage:
    python migrate.py              # Execute migration
    python migrate.py --dry-run    # Preview only (no file changes)
"""
import os
import sys
import shutil
import re
import csv
from pathlib import Path
from datetime import datetime

ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
DRY_RUN = "--dry-run" in sys.argv
MANIFEST = []  # (old_path, new_path, action)

def log(msg):
    print(f"  {'[DRY-RUN] ' if DRY_RUN else ''}  {msg}")

def record(old, new, action="COPY"):
    MANIFEST.append((str(old), str(new), action))

# ═══════════════════════════════════════════════════════════════════
# PHASE 1: FILE MAPPINGS
# ═══════════════════════════════════════════════════════════════════

# --- HTML Pages ---
HTML_MAP = {
    "index.html": "public/pages/index.html",
    "main.html": "public/pages/main.html",
    "about.html": "public/pages/about.html",
    "contact.html": "public/pages/contact.html",
    "blog.html": "public/pages/blog.html",
    "chat.html": "public/pages/chat.html",
    "faq.html": "public/pages/faq.html",
    "news.html": "public/pages/news.html",
    "sitemap.html": "public/pages/sitemap.html",
    "login.html": "public/pages/auth/login.html",
    "register.html": "public/pages/auth/register.html",
    "forgot-password.html": "public/pages/auth/forgot-password.html",
    "reset-password.html": "public/pages/auth/reset-password.html",
    "unauthorized.html": "public/pages/auth/unauthorized.html",
    "farmer.html": "public/pages/dashboards/farmer.html",
    "buyer.html": "public/pages/dashboards/buyer.html",
    "shopkeeper.html": "public/pages/dashboards/shopkeeper.html",
    "expert.html": "public/pages/dashboards/expert.html",
    "admin.html": "public/pages/dashboards/admin.html",
    "equipment.html": "public/pages/dashboards/equipment.html",
    "grocery.html": "public/pages/dashboards/grocery.html",
    "farm_dashboard.html": "public/pages/dashboards/farm_dashboard.html",
    "audit_dashboard.html": "public/pages/dashboards/audit_dashboard.html",
    "climate_dashboard.html": "public/pages/dashboards/climate_dashboard.html",
    "weather_dashboard.html": "public/pages/dashboards/weather_dashboard.html",
    "crisis_dashboard.html": "public/pages/dashboards/crisis_dashboard.html",
    "loan_dashboard.html": "public/pages/dashboards/loan_dashboard.html",
    "marketplace.html": "public/pages/marketplace/marketplace.html",
    "barter_exchange.html": "public/pages/marketplace/barter_exchange.html",
    "equipments.html": "public/pages/marketplace/equipments.html",
    "supply-chain.html": "public/pages/marketplace/supply-chain.html",
    "procurement_hub.html": "public/pages/marketplace/procurement_hub.html",
    "logistics_hub.html": "public/pages/marketplace/logistics_hub.html",
    "warehouse_control.html": "public/pages/marketplace/warehouse_control.html",
    "processing_hub.html": "public/pages/marketplace/processing_hub.html",
    "fleet_manager.html": "public/pages/marketplace/fleet_manager.html",
    "crop.html": "public/pages/farming/crop.html",
    "crop_advisory.html": "public/pages/farming/crop_advisory.html",
    "crop_rotation.html": "public/pages/farming/crop_rotation.html",
    "cropCalendar.html": "public/pages/farming/cropCalendar.html",
    "disease.html": "public/pages/farming/disease.html",
    "ai_disease.html": "public/pages/farming/ai_disease.html",
    "plantation.html": "public/pages/farming/plantation.html",
    "irrigation.html": "public/pages/farming/irrigation.html",
    "irrigation_control.html": "public/pages/farming/irrigation_control.html",
    "weather.html": "public/pages/farming/weather.html",
    "soil_portal.html": "public/pages/farming/soil_portal.html",
    "organic.html": "public/pages/farming/organic.html",
    "sustainable-farming.html": "public/pages/farming/sustainable-farming.html",
    "pest_suite.html": "public/pages/farming/pest_suite.html",
    "eco_toolbox.html": "public/pages/farming/eco_toolbox.html",
    "spatial.html": "public/pages/farming/spatial.html",
    "smart_loan.html": "public/pages/finance/smart_loan.html",
    "financial-support.html": "public/pages/finance/financial-support.html",
    "finance_bot.html": "public/pages/finance/finance_bot.html",
    "insurance_portal.html": "public/pages/finance/insurance_portal.html",
    "scheme.html": "public/pages/finance/scheme.html",
    "carbon_portal.html": "public/pages/finance/carbon_portal.html",
    "community_forum.html": "public/pages/community/community_forum.html",
    "favorites.html": "public/pages/community/favorites.html",
    "knowledge_hub.html": "public/pages/community/knowledge_hub.html",
    "labor_portal.html": "public/pages/community/labor_portal.html",
    "notifications.html": "public/pages/community/notifications.html",
    "trace.html": "public/pages/transparency/trace.html",
    "verify-produce.html": "public/pages/transparency/verify-produce.html",
    "transparency_portal.html": "public/pages/transparency/transparency_portal.html",
    "privacy-policy.html": "public/pages/legal/privacy-policy.html",
    "terms-and-conditions.html": "public/pages/legal/terms-and-conditions.html",
    "terms-and-service.html": "public/pages/legal/terms-and-service.html",
    "cookie-policy.html": "public/pages/legal/cookie-policy.html",
    "mission.html": "public/pages/misc/mission.html",
    "carrers.html": "public/pages/misc/carrers.html",
    "career.html": "public/pages/misc/career.html",
    "careers.html": "public/pages/misc/careers.html",
    "navbar.html": "public/pages/misc/navbar.html",
    "masthead.html": "public/pages/misc/masthead.html",
    "feed-back.html": "public/pages/misc/feed-back.html",
    "notfound.html": "public/pages/misc/notfound.html",
    "offline.html": "public/pages/misc/offline.html",
    "ThemeSelector.html": "public/pages/misc/ThemeSelector.html",
    "mobile-main.html": "public/pages/misc/mobile-main.html",
    "test-mobile.html": "public/pages/misc/test-mobile.html",
    "test-blog.html": "public/pages/misc/test-blog.html",
    "blog-backup.html": "public/pages/misc/blog-backup.html",
}

ROOT_CSS = [
    "about.css", "blog.css", "chat.css", "contact.css", "cropCalendar.css",
    "carrer.css", "disease.css", "faq.css", "farmer.css", "feed-back.css",
    "footer.css", "forum.css", "index.css", "knowledge_hub.css", "login.css",
    "main.css", "mission.css", "mobile-base.css", "mobile-main.css", "news.css",
    "organic.css", "plantation.css", "register.css", "responsive.css",
    "shopkeeper.css", "style.css", "styles.css", "terms-and-service.css",
    "theme.css", "weather.css", "weather-banner.css",
]
CSS_MAP = {f: f"public/css/{f}" for f in ROOT_CSS}
for f in ["eco_style.css", "irrigation.css", "pest_style.css", "rotation_planner.css", "spatial.css"]:
    CSS_MAP[f"css/{f}"] = f"public/css/{f}"
CSS_MAP["styles/switcher.css"] = "public/css/switcher.css"

ROOT_JS = [
    "ai_disease.js", "auth.js", "blog.js", "carbon_portal.js", "chat.js",
    "climate_dashboard.js", "crop_advisory.js", "cropCalendar.js", "disease.js",
    "equipment.js", "farm_dashboard.js", "farmer.js", "feed-back.js", "finance.js",
    "firebase.js", "fleet_manager.js", "forum.js", "index.js", "insurance_portal.js",
    "irrigation_control.js", "json-chatbot.js", "knowledge_hub.js", "labor_portal.js",
    "loan_dashboard.js", "login.js", "logistics_hub.js", "news.js", "organic.js",
    "plantation.js", "processing_hub.js", "procurement_hub.js", "register.js",
    "roadmap.js", "script.js", "service-worker.js", "shopkeeper.js", "soil_portal.js",
    "theme.js", "trace_batch.js", "translations.js", "voice-input.js",
    "warehouse_control.js", "weather.js", "weather-banner.js", "weather_dashboard.js",
]
JS_MAP = {f: f"public/js/{f}" for f in ROOT_JS}
for f in ["agri-helpers.js", "alert_manager.js", "eco_logic.js", "irrigation.js",
          "notifications.js", "pest_logic.js", "rotation_engine.js", "spatial.js"]:
    JS_MAP[f"js/{f}"] = f"public/js/{f}"
JS_MAP["javascript/i18n.js"] = "public/js/i18n.js"
JS_MAP["scripts/i18n.js"] = "public/js/i18n-extractor.js"

DATA_MAP = {
    "chatbot-responses.json": "public/data/chatbot-responses.json",
    "shopkeeper-data.json": "public/data/shopkeeper-data.json",
}

ML_DIR_MAP = {
    "Crop Yield Prediction": "ml/crop_yield_prediction",
    "Plant Disease Detection": "ml/plant_disease_detection",
    "Plant Seedlings Classification": "ml/plant_seedlings_classification",
    "Soil Classification Model": "ml/soil_classification_model",
    "Soil Classifier CNN": "ml/soil_classifier_cnn",
    "Fertiliser Recommendation System": "ml/fertiliser_recommendation",
    "tomato disease detection": "ml/tomato_disease_detection",
    "Disease prediction": "ml/disease_prediction_standalone",
}

TOOL_DIR_MAP = {
    "AgriBot_folder": "tools/agribot",
    "Community": "tools/community_app",
    "ExpenseFlow": "tools/expense_flow",
    "Crop_Planning": "tools/crop_planning",
    "Crop_Prices_Tracker": "tools/crop_prices_tracker",
    "Gov_schemes": "tools/gov_schemes",
    "Labour_Alerts": "tools/labour_alerts",
    "Forum": "tools/forum",
    "unlock mechanism": "tools/unlock_mechanism",
}

DOC_FILE_MAP = {
    "CHANGES_SUMMARY.md": "docs/CHANGES_SUMMARY.md",
    "CONTRIBUTION_SUMMARY.md": "docs/CONTRIBUTION_SUMMARY.md",
    "IMPLEMENTATION_SUMMARY.md": "docs/IMPLEMENTATION_SUMMARY.md",
    "SECURITY.md": "docs/security/SECURITY.md",
    "SECURITY_FIXES.md": "docs/security/SECURITY_FIXES.md",
    "PROPOSAL_FEATURE_ENHANCEMENTS.md": "docs/PROPOSAL_FEATURE_ENHANCEMENTS.md",
    "PULL_REQUEST.md": "docs/pr/PULL_REQUEST.md",
    "PULL_REQUEST_TEMPLATE.md": "docs/pr/PULL_REQUEST_TEMPLATE.md",
    "IPM_README.md": "docs/IPM_README.md",
    "SUSTAINABILITY_README.md": "docs/SUSTAINABILITY_README.md",
    "LEDGER_IMPLEMENTATION_GUIDE.md": "docs/guides/LEDGER_IMPLEMENTATION_GUIDE.md",
    "learn.md": "docs/learn.md",
}

JUNK_FILES = [
    ".git_diff.txt", ".git_status.txt", "diff.txt", "error.txt",
    "changes", "completed",
]

MODEL_MAP = {
    "face_vs_nonface_model.h5": "ml/models/face_vs_nonface_model.h5",
}

ALL_FILE_MAP = {}
ALL_FILE_MAP.update(HTML_MAP)
ALL_FILE_MAP.update(CSS_MAP)
ALL_FILE_MAP.update(JS_MAP)
ALL_FILE_MAP.update(DATA_MAP)
ALL_FILE_MAP.update(DOC_FILE_MAP)
ALL_FILE_MAP.update(MODEL_MAP)


# ═══════════════════════════════════════════════════════════════════
# PHASE 2: BUILD REFERENCE REWRITE MAP
# ═══════════════════════════════════════════════════════════════════

def build_ref_map():
    ref = {}
    for old, new in HTML_MAP.items():
        ref[old] = "/" + new.replace("public/", "", 1)
    for old, new in CSS_MAP.items():
        ref[old] = "/" + new.replace("public/", "", 1)
    for old, new in JS_MAP.items():
        ref[old] = "/" + new.replace("public/", "", 1)
    for old, new in DATA_MAP.items():
        ref[old] = "/" + new.replace("public/", "", 1)

    # Images
    images_dir = ROOT / "images"
    if images_dir.exists():
        for f in images_dir.iterdir():
            if f.is_file():
                ref[f"images/{f.name}"] = f"/images/{f.name}"

    # Assets
    assets_dir = ROOT / "assets"
    if assets_dir.exists():
        for f in assets_dir.iterdir():
            if f.is_file():
                ref[f"assets/{f.name}"] = f"/assets/{f.name}"

    return ref


# ═══════════════════════════════════════════════════════════════════
# PHASE 3: PATH REWRITING ENGINE
# ═══════════════════════════════════════════════════════════════════

def normalize_ref(value):
    if value.startswith("./"):
        return value[2:]
    return value

def is_external(value):
    return value.startswith(("http://", "https://", "data:", "#", "mailto:",
                             "tel:", "javascript:", "//", "{", "{{"))

def rewrite_html_content(content, ref_map):
    changes = 0
    def replace_attr(match):
        nonlocal changes
        prefix = match.group(1)
        quote = match.group(2)
        value = match.group(3)
        if is_external(value) or not value.strip():
            return match.group(0)
        cleaned = value
        if cleaned.startswith("/AgriTech/"):
            cleaned = cleaned[len("/AgriTech"):]
        normalized = normalize_ref(cleaned)
        if normalized in ref_map:
            changes += 1
            return f'{prefix}{quote}{ref_map[normalized]}{quote}'
        return match.group(0)

    pattern = r'((?:href|src|action|data-src|poster)\s*=\s*)(["\'])(.*?)\2'
    result = re.sub(pattern, replace_attr, content, flags=re.IGNORECASE)
    return result, changes

def rewrite_css_content(content, ref_map):
    changes = 0
    def replace_url(match):
        nonlocal changes
        prefix = match.group(1)
        quote = match.group(2) or ""
        value = match.group(3)
        suffix = match.group(4) or ""
        close = match.group(5)
        if is_external(value) or not value.strip():
            return match.group(0)
        normalized = normalize_ref(value)
        if normalized in ref_map:
            changes += 1
            return f'{prefix}{quote}{ref_map[normalized]}{suffix}{close}'
        return match.group(0)

    pattern = r'((?:@import\s+)?url\s*\()(["\']?)(.*?)(["\']?)(\))'
    result = re.sub(pattern, replace_url, content, flags=re.IGNORECASE)
    return result, changes

def rewrite_js_content(content, ref_map):
    changes = 0
    html_ref_map = {k: v for k, v in ref_map.items() if k.endswith(".html")}
    for old_ref, new_ref in html_ref_map.items():
        for q in ['"', "'"]:
            old_pattern = f'{q}{old_ref}{q}'
            new_pattern = f'{q}{new_ref}{q}'
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                changes += 1
    for old_ref, new_ref in ref_map.items():
        if old_ref.endswith(".json") and not old_ref.startswith("http"):
            for q in ['"', "'"]:
                old_pattern = f'{q}{old_ref}{q}'
                new_pattern = f'{q}{new_ref}{q}'
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes += 1
    return content, changes


# ═══════════════════════════════════════════════════════════════════
# PHASE 4: FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def copy_file(old_rel, new_rel):
    src = ROOT / old_rel
    dst = ROOT / new_rel
    if not src.exists():
        log(f"SKIP (not found): {old_rel}")
        return False
    if not DRY_RUN:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
    record(old_rel, new_rel, "COPY")
    log(f"COPY: {old_rel} -> {new_rel}")
    return True

def copy_directory(old_rel, new_rel):
    src = ROOT / old_rel
    dst = ROOT / new_rel
    if not src.exists():
        log(f"SKIP DIR (not found): {old_rel}")
        return False
    if not DRY_RUN:
        if dst.exists():
            shutil.rmtree(str(dst))
        shutil.copytree(str(src), str(dst))
    record(old_rel, new_rel, "COPY_DIR")
    log(f"COPY DIR: {old_rel} -> {new_rel}")
    return True

def delete_file(rel_path):
    f = ROOT / rel_path
    if not f.exists():
        return
    if not DRY_RUN:
        f.unlink()
    record(rel_path, "(deleted)", "DELETE")
    log(f"DELETE: {rel_path}")

def delete_empty_dir(rel_path):
    d = ROOT / rel_path
    if d.exists() and d.is_dir():
        try:
            if not DRY_RUN:
                d.rmdir()
            log(f"DELETE DIR: {rel_path}")
        except OSError:
            log(f"SKIP DIR (not empty): {rel_path}")


# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print(f"  AgriTech Migration {'(DRY RUN)' if DRY_RUN else '(LIVE)'}")
    print(f"  Root: {ROOT}")
    print(f"  Time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Step 1: Create directory structure
    print("\n[1/7] Creating directory structure...")
    dirs = [
        "public/pages", "public/pages/auth", "public/pages/dashboards",
        "public/pages/marketplace", "public/pages/farming", "public/pages/finance",
        "public/pages/community", "public/pages/transparency", "public/pages/legal",
        "public/pages/misc",
        "public/css", "public/js", "public/images", "public/assets", "public/data",
        "ml", "ml/models", "tools",
        "docs/security", "docs/pr", "docs/guides", "docs/features", "docs/api",
    ]
    for d in dirs:
        if not DRY_RUN:
            (ROOT / d).mkdir(parents=True, exist_ok=True)

    # Step 2: Copy individual files
    print("\n[2/7] Copying files to new locations...")
    for old, new in ALL_FILE_MAP.items():
        copy_file(old, new)

    # Step 3: Copy directories
    print("\n[3/7] Copying directories...")
    copy_directory("images", "public/images")
    copy_directory("assets", "public/assets")

    for old, new in ML_DIR_MAP.items():
        copy_directory(old, new)

    for old, new in TOOL_DIR_MAP.items():
        copy_directory(old, new)

    # Consolidate docs
    existing_docs = {
        "docs/API_VERSIONING.md": "docs/api/API_VERSIONING.md",
        "docs/GEWS_FEATURE.md": "docs/features/GEWS_FEATURE.md",
        "docs/TRACEABILITY_FEATURE.md": "docs/features/TRACEABILITY_FEATURE.md",
        "docs/SPATIAL_ANALYTICS_IMPLEMENTATION.md": "docs/features/SPATIAL_ANALYTICS_IMPLEMENTATION.md",
        "docs/PR_SUMMARY_GEWS.md": "docs/pr/PR_SUMMARY_GEWS.md",
        "docs/QUICK_START_GEWS.md": "docs/guides/QUICK_START_GEWS.md",
        "docs/QUICK_START_TRACEABILITY.md": "docs/guides/QUICK_START_TRACEABILITY.md",
        "docs/SECURITY_IMPLEMENTATION.md": "docs/security/SECURITY_IMPLEMENTATION.md",
    }
    for old, new in existing_docs.items():
        copy_file(old, new)
    for old, new in DOC_FILE_MAP.items():
        copy_file(old, new)

    # Step 4: Rewrite paths
    print("\n[4/7] Rewriting internal paths...")
    ref_map = build_ref_map()
    total_changes = 0

    # Rewrite HTML files
    for old, new in HTML_MAP.items():
        filepath = ROOT / new
        if not filepath.exists():
            continue
        content = filepath.read_text(encoding="utf-8", errors="replace")
        new_content, c1 = rewrite_html_content(content, ref_map)
        new_content, c2 = rewrite_css_content(new_content, ref_map)
        new_content, c3 = rewrite_js_content(new_content, ref_map)
        changes = c1 + c2 + c3
        if changes > 0 and not DRY_RUN:
            filepath.write_text(new_content, encoding="utf-8")
        if changes > 0:
            log(f"REWRITE HTML: {new} ({changes} changes)")
        total_changes += changes

    # Rewrite CSS files
    for old, new in CSS_MAP.items():
        filepath = ROOT / new
        if not filepath.exists():
            continue
        content = filepath.read_text(encoding="utf-8", errors="replace")
        new_content, changes = rewrite_css_content(content, ref_map)
        if changes > 0 and not DRY_RUN:
            filepath.write_text(new_content, encoding="utf-8")
        if changes > 0:
            log(f"REWRITE CSS: {new} ({changes} changes)")
        total_changes += changes

    # Rewrite JS files
    for old, new in JS_MAP.items():
        filepath = ROOT / new
        if not filepath.exists():
            continue
        content = filepath.read_text(encoding="utf-8", errors="replace")
        new_content, changes = rewrite_js_content(content, ref_map)
        if changes > 0 and not DRY_RUN:
            filepath.write_text(new_content, encoding="utf-8")
        if changes > 0:
            log(f"REWRITE JS: {new} ({changes} changes)")
        total_changes += changes

    print(f"\n  Total path rewrites: {total_changes}")

    # Step 5: Delete junk files
    print("\n[5/7] Deleting junk files...")
    for f in JUNK_FILES:
        delete_file(f)
    delete_empty_dir("AgriTech")

    # Step 6: Generate manifest
    print("\n[6/7] Generating manifest...")
    manifest_path = ROOT / "migration_manifest.csv"
    if not DRY_RUN:
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["old_path", "new_path", "action"])
            for row in MANIFEST:
                writer.writerow(row)

    # Step 7: Summary
    print("\n[7/7] Summary")
    print("=" * 60)
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'EXECUTED'}")
    print(f"  Files copied: {sum(1 for r in MANIFEST if r[2] == 'COPY')}")
    print(f"  Dirs copied: {sum(1 for r in MANIFEST if r[2] == 'COPY_DIR')}")
    print(f"  Files deleted: {sum(1 for r in MANIFEST if r[2] == 'DELETE')}")
    print(f"  Path rewrites: {total_changes}")
    if not DRY_RUN:
        print(f"  Manifest: {manifest_path}")
    print("=" * 60)

    if not DRY_RUN:
        print("\nREMAINING: Update server.js and app.py manually.")
        print("  Original files preserved — clean up after verification.")


if __name__ == "__main__":
    main()
