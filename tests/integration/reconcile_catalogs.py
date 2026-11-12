import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FRONTEND_CATALOGS = [
    ("Amazon", "src/backend/scraped_data/amazon_products.json"),
    ("Apple", "src/backend/brand_scrapers/apple/scraped_data/apple_products.json"),
    ("Vivo", "src/backend/brand_scrapers/vivo/scraped_data/vivo_products.json"),
    ("Croma", "src/backend/brand_scrapers/croma/scraped_data/croma_products.json"),
    ("Samsung", "src/backend/brand_scrapers/samsung/scraped_data/samsung_products.json"),
    ("Reliance", "src/backend/brand_scrapers/reliance/scraped_data/reliance_products.json"),
    ("JioMart", "src/backend/brand_scrapers/jiomart/scraped_data/jiomart_products.json"),
    ("Oppo", "src/backend/brand_scrapers/oppo/scraped_data/oppo_products.json"),
    ("Flipkart", "src/backend/scraped_data/flipkart_products.json"),
]

OTHER_FILES = [
    ("Amazon (brand_scrapers)", "src/backend/brand_scrapers/amazon/scraped_data/amazon_products.json"),
    ("Flipkart (brand_scrapers)", "src/backend/brand_scrapers/flipkart/scraped_data/flipkart_products.json"),
    ("Apple (intelligence)", "src/backend/brand_scrapers/apple/apple_intelligence/scraped_data/apple_products.json"),
]

def main():
    print("=== 1. FRONTEND BUNDLED CATALOGS (searchService.js) ===")
    fe_total_raw = 0
    fe_total_valid = 0
    all_products_merged = []
    provider_stats = {}

    for name, rel_path in FRONTEND_CATALOGS:
        full_p = os.path.join(PROJECT_ROOT, rel_path)
        if not os.path.exists(full_p):
            print(f"[{name}] File NOT found: {rel_path}")
            continue
        with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        raw_count = len(data) if isinstance(data, list) else 0
        fe_total_raw += raw_count
        
        valid_count = 0
        unique_names = set()
        for item in (data if isinstance(data, list) else []):
            n = item.get("name") or item.get("title") or item.get("model") or ""
            p = item.get("price") or item.get("price_num")
            if n.strip() and p:
                valid_count += 1
                unique_names.add(n.strip().lower())
                all_products_merged.append((name, n.strip(), p))
                
        dup_within_provider = raw_count - len(unique_names)
        provider_stats[name] = {
            "path": rel_path,
            "raw_count": raw_count,
            "valid_count": valid_count,
            "unique_names_count": len(unique_names),
            "internal_duplicates": dup_within_provider
        }
        print(f"{name:12} | Raw: {raw_count:4} | Valid: {valid_count:4} | Unique Titles: {len(unique_names):4} | Dups: {dup_within_provider:3} | {rel_path}")

    print(f"\nFrontend Total Raw Items: {fe_total_raw}")

    print("\n=== 2. OTHER BACKEND SCRAPED_DATA FILES ===")
    for name, rel_path in OTHER_FILES:
        full_p = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_p):
            with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            c = len(data) if isinstance(data, list) else 0
            print(f"{name:25} | Items: {c:4} | {rel_path}")

    print("\n=== 3. CROSS-PROVIDER DEDUPLICATION ANALYSIS ===")
    merged_titles = set()
    cross_dups = 0
    for prov, title, price in all_products_merged:
        t_clean = title.lower()
        if t_clean in merged_titles:
            cross_dups += 1
        else:
            merged_titles.add(t_clean)

    print(f"Total Combined Products Across All 9 Frontends: {len(all_products_merged)}")
    print(f"Unique Product Titles Across Entire Platform: {len(merged_titles)}")
    print(f"Cross-Store Overlapping Titles: {cross_dups}")

    print("\n=== 4. RECONCILIATION OF 1,360 vs 1,320 REPORTED FIGURES ===")
    calc_with_fe_flipkart = 510 + 58 + 13 + 4 + 488 + 5 + 186 + 54 + 93
    calc_with_scraper_flipkart = 510 + 58 + 13 + 4 + 488 + 5 + 186 + 54 + 2
    print(f"Sum if using frontend's flipkart (93 items): {calc_with_fe_flipkart}")
    print(f"Sum if using flipkart_scraper's flipkart (2 items): {calc_with_scraper_flipkart}")

    return fe_total_raw > 0 and len(merged_titles) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
