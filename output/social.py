def format_instagram(lead) -> str:
    return ", ".join(lead.social_profiles or []) or "Not informed"