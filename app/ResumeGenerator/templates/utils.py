from pathlib import Path

def escape_latex(text: str) -> str:
    """Escape special LaTeX characters
    
    Order matters: escape #, $, &, % first (before backslash replacement)
    to avoid conflicts with LaTeX commands.
    """
    if not text:
        return ""
    # First pass: escape characters that need escaping before backslash
    # These are critical for LaTeX compilation
    text = text.replace('#', r'\#')
    text = text.replace('$', r'\$')
    text = text.replace('&', r'\&')
    text = text.replace('%', r'\%')
    text = text.replace('^', r'\textasciicircum{}')
    text = text.replace('_', r'\_')
    
    # Second pass: escape braces (these can appear after backslash replacement)
    text = text.replace('{', r'\{')
    text = text.replace('}', r'\}')
    
    # Third pass: escape backslash and tilde (after other special chars)
    text = text.replace('\\', r'\textbackslash{}')
    text = text.replace('~', r'\textasciitilde{}')
    
    return text

def format_date_for_latex(date) -> str:
    """Format date string (YYYY-MM-DD) or datetime object for LaTeX output"""
    if not date or date == 'None' or date == '':
        return 'Present'
    
    # Handle datetime objects
    if hasattr(date, 'strftime'):
        date = date.strftime('%Y-%m-%d')
    
    # Convert to string if not already
    date_str = str(date)
    
    try:
        year, month, day = date_str.split('-')
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{month_names[int(month) - 1]} {day}, {year}"
    except (ValueError, IndexError, AttributeError):
        # If date format is invalid, return as-is
        return str(date)

def read_template_file(filename: str) -> str:
    """Read a template file from the same directory as this file"""
    current_file = Path(__file__)
    template_path = current_file.parent / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    return template_path.read_text(encoding='utf-8')