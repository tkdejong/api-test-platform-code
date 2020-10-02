def preprocess_exclude_admin_path(endpoints, **kwargs):
    """
    Filter out the admin urls from mobetta
    """
    return [
        (path, path_regex, method, callback) for path, path_regex, method, callback in endpoints
        if not path.startswith("/admin/")
    ]
