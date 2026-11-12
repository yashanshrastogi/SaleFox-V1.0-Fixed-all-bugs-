import os
import sys
import json

# Add src/backend to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "backend"))
from unified_automation import validate_checkout_request

test_cases = [
    {
        "name": "1. Unconfigured empty payload (No .env or payload)",
        "payload": {},
        "expected_valid": False,
        "expected_reason": "Missing required fields"
    },
    {
        "name": "2. Missing customer name",
        "payload": {
            "customer_phone": "9812345678",
            "customer_email": "demo.user@company.org",
            "delivery_address": "Flat 402, Green Avenue, Sector 15",
            "delivery_pincode": "110001"
        },
        "expected_valid": False,
        "expected_reason": "customer_name"
    },
    {
        "name": "3. Placeholder customer name ('SaleFox Customer')",
        "payload": {
            "customer_name": "SaleFox Customer",
            "customer_phone": "9812345678",
            "customer_email": "demo.user@company.org",
            "delivery_address": "Flat 402, Green Avenue, Sector 15",
            "delivery_pincode": "110001"
        },
        "expected_valid": False,
        "expected_reason": "placeholder value detected"
    },
    {
        "name": "4. Placeholder phone number ('9876543210')",
        "payload": {
            "customer_name": "Rohan Sharma",
            "customer_phone": "9876543210",
            "customer_email": "rohan.sharma@domain.in",
            "delivery_address": "Flat 402, Green Avenue, Sector 15",
            "delivery_pincode": "110001"
        },
        "expected_valid": False,
        "expected_reason": "placeholder test number is not permitted"
    },
    {
        "name": "5. Invalid phone number (too short / invalid prefix)",
        "payload": {
            "customer_name": "Rohan Sharma",
            "customer_phone": "12345",
            "customer_email": "rohan.sharma@domain.in",
            "delivery_address": "Flat 402, Green Avenue, Sector 15",
            "delivery_pincode": "110001"
        },
        "expected_valid": False,
        "expected_reason": "must be a valid 10-digit Indian mobile number"
    },
    {
        "name": "6. Placeholder email address ('customer@example.com')",
        "payload": {
            "customer_name": "Rohan Sharma",
            "customer_phone": "9811223344",
            "customer_email": "customer@example.com",
            "delivery_address": "Flat 402, Green Avenue, Sector 15",
            "delivery_pincode": "110001"
        },
        "expected_valid": False,
        "expected_reason": "placeholder example.com address is not permitted"
    },
    {
        "name": "7. Invalid PIN code ('012345' or '1234')",
        "payload": {
            "customer_name": "Rohan Sharma",
            "customer_phone": "9811223344",
            "customer_email": "rohan.sharma@domain.in",
            "delivery_address": "Flat 402, Green Avenue, Sector 15",
            "delivery_pincode": "01234"
        },
        "expected_valid": False,
        "expected_reason": "must be a valid 6-digit Indian postal PIN code"
    },
    {
        "name": "8. Disallowed legacy hardcoded address ('Himalayan Colony...')",
        "payload": {
            "customer_name": "Rohan Sharma",
            "customer_phone": "9811223344",
            "customer_email": "rohan.sharma@domain.in",
            "delivery_address": "Himalayan Colony, Himalayan Appt, Haripur Kalan",
            "delivery_pincode": "249205"
        },
        "expected_valid": False,
        "expected_reason": "disallowed legacy placeholder address detected"
    },
    {
        "name": "9. Inspection mode (read-only; no customer details required)",
        "payload": {
            "automation_mode": "inspection",
            "product_url": "https://www.apple.com/in/shop/buy-iphone/iphone-16"
        },
        "expected_valid": True,
        "expected_reason": "Inspection mode"
    },
    {
        "name": "10. Valid synthetic demo profile in dry_run mode",
        "payload": {
            "automation_mode": "dry_run",
            "customer_name": "Rohan Sharma",
            "customer_phone": "+91 9811223344",
            "customer_email": "rohan.sharma@audit-domain.in",
            "delivery_address": "Tower 4, Flat 12B, Cyber City View, DLF Phase 2",
            "delivery_city": "Gurugram",
            "delivery_state": "Haryana",
            "delivery_pincode": "122002"
        },
        "expected_valid": True,
        "expected_reason": "validated successfully in 'dry_run' mode"
    },
    {
        "name": "11. Production mode without explicit user_confirmed",
        "payload": {
            "automation_mode": "production",
            "customer_name": "Rohan Sharma",
            "customer_phone": "+91 9811223344",
            "customer_email": "rohan.sharma@audit-domain.in",
            "delivery_address": "Tower 4, Flat 12B, Cyber City View, DLF Phase 2",
            "delivery_pincode": "122002"
        },
        "expected_valid": False,
        "expected_reason": "Production mode requires explicit 'user_confirmed'"
    },
    {
        "name": "12. Production mode with user_confirmed: true",
        "payload": {
            "automation_mode": "production",
            "user_confirmed": True,
            "customer_name": "Rohan Sharma",
            "customer_phone": "+91 9811223344",
            "customer_email": "rohan.sharma@audit-domain.in",
            "delivery_address": "Tower 4, Flat 12B, Cyber City View, DLF Phase 2",
            "delivery_pincode": "122002"
        },
        "expected_valid": True,
        "expected_reason": "validated successfully in 'production' mode"
    }
]

def run_tests():
    passed_count = 0
    failed_count = 0
    log_lines = []

    for tc in test_cases:
        is_valid, reason, _ = validate_checkout_request(tc["payload"])
        matched = (is_valid == tc["expected_valid"]) and (tc["expected_reason"].lower() in reason.lower())
        status = "PASS" if matched else "FAIL"
        if matched:
            passed_count += 1
        else:
            failed_count += 1
        line = f"[{status}] {tc['name']}\n       Result: is_valid={is_valid}, msg='{reason}'"
        print(line)
        log_lines.append(line)

    print(f"\nSummary: {passed_count}/{len(test_cases)} Passed, {failed_count} Failed")
    return passed_count == len(test_cases)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

