import re

def sanitize_input(text, max_length=None):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text

def validate_required_fields(data, required_fields):
    """Validate that a mapping contains non-empty required fields."""
    if not isinstance(data, dict):
        return False, "Invalid request payload"

    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"Missing required field: {field}"
    return True, "Valid input"


def validate_input(data, required_fields=None):
    """Validate input data structure and optionally required fields."""
    if not isinstance(data, dict) or not data:
        return False, "No data provided"

    if required_fields:
        return validate_required_fields(data, required_fields)

    return True, "Valid input"


def validate_email(email, gmail_only=False):
    """Validate an email address and optionally enforce gmail-only logins."""
    if not isinstance(email, str):
        return False, "Email is required"

    email = email.strip().lower()
    if not email:
        return False, "Email is required"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Please enter a valid email address"

    if gmail_only and not email.endswith("@gmail.com"):
        return False, "Please use a @gmail.com address"

    return True, "Valid email"


def validate_username(username, min_length=3, max_length=30):
    """Validate a username-like identifier."""
    if not isinstance(username, str):
        return False, "Username is required"

    username = username.strip()
    if not username:
        return False, "Username is required"

    if len(username) < min_length or len(username) > max_length:
        return False, f"Username must be between {min_length} and {max_length} characters"

    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return False, "Username can only contain letters, numbers, dots, underscores, and hyphens"

    return True, "Valid username"


def validate_full_name(full_name, max_length=100):
    """Validate a person's full name."""
    if not isinstance(full_name, str):
        return False, "Full name is required"

    full_name = full_name.strip()
    if not full_name:
        return False, "Full name is required"

    if len(full_name) > max_length:
        return False, f"Full name must be at most {max_length} characters"

    if not re.match(r"^[A-Za-z\s.'-]+$", full_name):
        return False, "Full name can only contain letters, spaces, periods, apostrophes, and hyphens"

    return True, "Valid full name"


def validate_password_strength(password, min_length=8, require_special=False):
    """Validate password strength for auth forms."""
    if not isinstance(password, str) or not password:
        return False, "Password is required"

    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, "Valid password"


def validate_role(role, allowed_roles):
    """Validate that a role belongs to an allowed set."""
    if not isinstance(role, str):
        return False, "Role is required"

    normalized_role = role.strip().lower()
    if not normalized_role:
        return False, "Role is required"

    if normalized_role not in allowed_roles:
        return False, "Invalid role selected"

    return True, normalized_role


def validate_numeric_range(value, min_value=None, max_value=None, field_name="value"):
    """Validate a numeric input and enforce optional range checks."""
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return False, f"{field_name} must be a number"

    if min_value is not None and number < min_value:
        return False, f"{field_name} must be at least {min_value}"

    if max_value is not None and number > max_value:
        return False, f"{field_name} must be at most {max_value}"

    return True, number
