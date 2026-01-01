from pathlib import Path

def escape_latex(text: str) -> str:
    """Escape special LaTeX characters
    
    Properly escapes all LaTeX special characters, handling edge cases.
    """
    if not text:
        return ""
    
    # Convert to string to handle any type
    text = str(text)
    
    import re
    
    # Strategy: Use regex with negative lookbehind to avoid double-escaping
    # This ensures we don't escape characters that are already escaped
    
    # STEP 1: Escape special characters that are NOT already escaped
    # Negative lookbehind (?<!\\) means "not preceded by backslash"
    text = re.sub(r'(?<!\\)&', r'\\&', text)
    text = re.sub(r'(?<!\\)#', r'\\#', text)
    text = re.sub(r'(?<!\\)%', r'\\%', text)
    text = re.sub(r'(?<!\\)\$', r'\\$', text)
    text = re.sub(r'(?<!\\)\^', r'\\textasciicircum{}', text)
    text = re.sub(r'(?<!\\)_', r'\\_', text)
    text = re.sub(r'(?<!\\)\{', r'\\{', text)
    text = re.sub(r'(?<!\\)\}', r'\\}', text)
    text = re.sub(r'(?<!\\)~', r'\\textasciitilde{}', text)
    
    # STEP 2: Escape backslashes that are NOT part of valid LaTeX escape sequences
    # Match backslash that is NOT followed by a valid escape character
    # Valid escape chars: #, &, %, $, ^, _, {, }, ~, \, and common LaTeX commands
    # We want to escape standalone backslashes, not those in "\#", "\&", etc.
    text = re.sub(r'\\(?![#&$%_{}~\\a-zA-Z])', r'\\textbackslash{}', text)
    
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