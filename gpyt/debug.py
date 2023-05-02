from gpyt import DEBUG


def debug(string: str, **kwargs):
    """
    Debug function reading DEBUG env variable.

    Always flush.
    """
    if not DEBUG:
        return
    print(f"🐛: {string}", flush=True, **kwargs)
