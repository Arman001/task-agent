import os

SAFE_TOOLS = {
    "calculator",
    "text_analyzer",
    "file_reader",
    "file_checker",
    "web_search",
    "api_weather"
}

MODERATE_TOOLS = {
    "file_writer",
    "url_fetch"
}

CRITICAL_TOOLS = {
    # Often an HTTP tool could be critical if using POST, but we will check keywords
}

CRITICAL_KEYWORDS = [
    "delete", "remove", "rm", "destroy", "drop",
    "post", "put", "patch", "execute", "exec"
]

def classify_action(step_description: str, tool_name: str = "") -> str:
    """Classifies an action as SAFE, MODERATE, or CRITICAL."""
    # Check keywords in description
    desc_lower = step_description.lower()
    for keyword in CRITICAL_KEYWORDS:
        # Match as whole words or prefix where necessary, a simple 'in' check is safest to be conservative
        # e.g. "delete file.txt" -> critical
        if f" {keyword} " in f" {desc_lower} " or desc_lower.startswith(f"{keyword} "):
            return "CRITICAL"

    if tool_name in SAFE_TOOLS:
        return "SAFE"
    elif tool_name in MODERATE_TOOLS:
        return "MODERATE"
    elif tool_name in CRITICAL_TOOLS:
        return "CRITICAL"
    
    # Check for HTTP method in step description if it's an HTTP request
    if tool_name == "http_request":
        if "post " in desc_lower or "put " in desc_lower or "delete " in desc_lower or "patch " in desc_lower:
            return "CRITICAL"
        else:
            return "SAFE" # Assuming GET is default and safe

    # Default conservative
    return "MODERATE"
