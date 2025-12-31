from pathlib import Path

def escape_latex(text: str) -> str:
    """Escape special LaTeX characters"""
    if not text:
        return ""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '^': r'\textasciicircum{}',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
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