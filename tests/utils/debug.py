import json

def show_debug(expected_status=None, expected_text=None, res=None):
    print("\n================ DEBUG OUTPUT ================")

    if expected_status is not None:
        print(f"EXPECTED STATUS: {expected_status}")
    print(f"ACTUAL STATUS:   {res.status_code}")

    print("\n----- RAW RESPONSE BODY -----")
    print(res.get_data(as_text=True))

    print("\n----- PARSED JSON (if valid) -----")
    try:
        print(json.dumps(res.get_json(), indent=2))
    except Exception:
        print("JSON PARSE FAILED")

    if expected_text:
        print("\n----- EXPECTED SUBSTRING -----")
        print(expected_text)

    print("==============================================\n")
