"""
HTML email template for RealtorOS follow-up emails.

This template provides a professional, responsive HTML structure
with a header, body placeholder, and footer signature.
"""

EMAIL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Follow-up Email</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {font-family: Arial, sans-serif !important;}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 40px 20px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600; line-height: 1.3;">
                                            Real Estate Follow-up
                                        </h1>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 30px 40px; color: #333333; font-size: 16px; line-height: 1.6;">
                            {email_body}
                        </td>
                    </tr>
                    
                    <!-- Footer/Signature -->
                    <tr>
                        <td style="padding: 20px 40px 30px 40px; background-color: #f9f9f9; border-top: 1px solid #e5e5e5; border-radius: 0 0 8px 8px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="padding-bottom: 15px;">
                                        <p style="margin: 0; color: #333333; font-size: 16px; font-weight: 500;">
                                            Best regards,
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <p style="margin: 0; color: #333333; font-size: 16px; font-weight: 600;">
                                            {agent_name}
                                        </p>
                                    </td>
                                </tr>
                                {agent_title_row}
                                {company_row}
                                {phone_row}
                                <tr>
                                    <td style="padding-top: 10px;">
                                        <p style="margin: 0; color: #666666; font-size: 14px;">
                                            Email: <a href="mailto:{agent_email}" style="color: #667eea; text-decoration: none;">{agent_email}</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

def format_email_html(
    email_body: str,
    agent_name: str,
    agent_title: str = None,
    agent_company: str = None,
    agent_phone: str = None,
    agent_email: str = ""
) -> str:
    """
    Format email body with HTML template.
    
    Args:
        email_body: The main email body content (plain text or HTML)
        agent_name: Agent's full name
        agent_title: Agent's title (optional)
        agent_company: Agent's company name (optional)
        agent_phone: Agent's phone number (optional)
        agent_email: Agent's email address
        
    Returns:
        Complete HTML email string
    """
    # Handle None or empty email_body
    if not email_body:
        email_body = ""
    
    # Convert plain text body to HTML paragraphs if needed
    import re
    email_body_str = str(email_body).strip()
    
    # Check if the body already contains HTML tags
    # Look for HTML tags (e.g., <p>, <div>, <h1>, etc.)
    has_html_tags = bool(re.search(r'<[a-z][\s\S]*?>', email_body_str, re.IGNORECASE))
    
    if has_html_tags:
        # Already contains HTML tags, use as-is (don't wrap in <p> tags)
        html_body = email_body_str
    else:
        # Convert plain text to HTML paragraphs
        paragraphs = email_body_str.split('\n\n')
        html_body = '\n'.join([
            f'<p style="margin: 0 0 16px 0; color: #333333;">{p.replace(chr(10), "<br>")}</p>'
            for p in paragraphs if p.strip()
        ])
    
    # Build agent title row if provided
    agent_title_row = ""
    if agent_title:
        agent_title_row = f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <p style="margin: 0; color: #666666; font-size: 14px;">
                                            {agent_title}
                                        </p>
                                    </td>
                                </tr>"""
    
    # Build company row if provided
    company_row = ""
    if agent_company:
        company_row = f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <p style="margin: 0; color: #666666; font-size: 14px;">
                                            {agent_company}
                                        </p>
                                    </td>
                                </tr>"""
    
    # Build phone row if provided
    phone_row = ""
    if agent_phone:
        phone_row = f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <p style="margin: 0; color: #666666; font-size: 14px;">
                                            Phone: <a href="tel:{agent_phone}" style="color: #667eea; text-decoration: none;">{agent_phone}</a>
                                        </p>
                                    </td>
                                </tr>"""
    
    # Format the template - escape any curly braces in content to prevent format errors
    # Escape braces in the content (but not the template placeholders)
    escaped_html_body = html_body.replace('{', '{{').replace('}', '}}')
    escaped_agent_title_row = agent_title_row.replace('{', '{{').replace('}', '}}')
    escaped_company_row = company_row.replace('{', '{{').replace('}', '}}')
    escaped_phone_row = phone_row.replace('{', '{{').replace('}', '}}')
    
    # Now use .format() which will work correctly with escaped content
    html_email = EMAIL_HTML_TEMPLATE.format(
        email_body=escaped_html_body,
        agent_name=agent_name or "Real Estate Agent",
        agent_title_row=escaped_agent_title_row,
        company_row=escaped_company_row,
        phone_row=escaped_phone_row,
        agent_email=agent_email or ""
    )
    
    return html_email

