def _create_leads(
    batches: list[tuple[dict, list[dict]]],
    selected: list[dict],
) -> list:
    from core.models.lead_model import Lead
    objects = {}
    for region, elements in batches:
        for element in elements:
            if element.get("type") not in {"node", "way", "relation"}:
                continue
            identifier = f"osm:{element['type']}:{element['id']}"
            if identifier not in objects:
                objects[identifier] = {
                    "region": region,
                    "tags": {},
                }
            tags = objects[identifier]["tags"]
            for key, value in element.get("tags", {}).items():
                if value and not tags.get(key):
                    tags[key] = value
    leads = []
    for item in objects.values():
        tags = item["tags"]
        region = item["region"]
        name = tags.get("name")
        if not name:
            continue
        matched = [
            category["label"]
            for category in selected
            if any(
                tags.get(condition["key"]) == condition["value"]
                for condition in category["filters"]
            )
        ]
        if not matched:
            continue
        social_profiles = []
        for key in ("contact:instagram", "instagram"):
            value = tags.get(key)
            if value:
                profile = value.strip()
                if profile and profile not in social_profiles:
                    social_profiles.append(profile)
        leads.append(Lead(
            social_profiles=social_profiles,
            name=name,
            category=", ".join(matched),
            location=f"{region['city']}, {region['state']}",
            website=(
                tags.get("website")
                or tags.get("contact:website")
            ),
            phone=(
                tags.get("phone")
                or tags.get("contact:phone")
            ),
        ))
    return leads
