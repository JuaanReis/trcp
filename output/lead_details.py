from output.social import format_instagram

def show_lead(lead, index=None):
    title = f"{index}. {lead.name}" if index is not None else lead.name
    print(title)
    print(f"   Category: {lead.category}")
    print(f"   Location: {lead.location}")
    print(f"   Website: {lead.website or 'Not informed'}")
    print(f"   Phone: {lead.phone or 'Not informed'}")
    print(f"   Instagram: {format_instagram(lead)}")
    print(f"   Status: {lead.status}")
    print(f"   Score: {lead.score:.2f}")
    print(f"   Created: {lead.created_at:%d/%m/%Y %H:%M}")
    print()
