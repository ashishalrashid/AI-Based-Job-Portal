from .debug import show_debug

def assert_response(res, expected_status=None, expected_message=None):
    """
    Universal assertion for response objects.
    Automatically prints debug info when failing.
    """

    # Print debug if status is wrong
    if expected_status is not None and res.status_code != expected_status:
        show_debug(expected_status=expected_status, res=res)

    assert expected_status is None or res.status_code == expected_status

    # If expecting text inside response JSON
    if expected_message:
        body = ""
        try:
            body = res.get_json()
        except:
            body = res.get_data(as_text=True)

        if expected_message.lower() not in str(body).lower():
            show_debug(expected_status, expected_message, res)
        assert expected_message.lower() in str(body).lower()
