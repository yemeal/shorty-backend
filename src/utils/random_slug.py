import secrets


def generate_random_slug():
    slug = secrets.token_urlsafe(4)
    return slug
