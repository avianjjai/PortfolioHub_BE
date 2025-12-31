import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Path to the Resume template directory (relative to server directory)
# Try multiple possible paths
def get_resume_template_dir():
    """Get the path to the Resume template directory"""
    current_file = Path(__file__)
    # Try: server/app/utils/latex_resume_generator.py -> Portfolio/Resume
    possible_paths = [
        current_file.parent.parent.parent.parent / "Resume",  # From server/app/utils/
        current_file.parent.parent.parent / "Resume",  # Alternative
        Path.cwd().parent / "Resume",  # From server/ directory
        Path.cwd() / "Resume",  # If running from Portfolio root
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "Template.tex").exists():
            return path
    
    # Return the most likely path even if it doesn't exist (for error message)
    return possible_paths[0]

RESUME_TEMPLATE_DIR = get_resume_template_dir()

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

def format_date_for_latex(date_str: Optional[str]) -> str:
    """Format date string for LaTeX (e.g., '2023-01-15' -> 'Jan 2023')"""
    if not date_str:
        return ""
    try:
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                return date_obj.strftime('%b %Y')
            except:
                continue
        # If it's an integer (like project start_date), treat as year
        if isinstance(date_str, (int, str)) and str(date_str).isdigit() and len(str(date_str)) == 4:
            return str(date_str)
        return str(date_str)
    except:
        return str(date_str)

def generate_title_section(user_data: Dict) -> str:
    """Generate Title.tex content"""
    first_name = escape_latex(user_data.get('first_name', ''))
    last_name = escape_latex(user_data.get('last_name', ''))
    full_name = f"{first_name} {last_name}".strip() or escape_latex(user_data.get('username', 'User'))
    
    location = escape_latex(user_data.get('address', ''))
    phone = escape_latex(user_data.get('phone', ''))
    email = escape_latex(user_data.get('email', ''))
    linkedin = user_data.get('linkedin_url', '')
    github = user_data.get('github_url', '')
    website = user_data.get('website_url', '')
    leetcode = user_data.get('leetcode_url', '')
    
    title_content = "\\begin{center}\n"
    title_content += "    {\\Huge \\scshape " + full_name + "}\\\\\n"
    title_content += "    \\vspace{2pt}\n"
    
    if location:
        title_content += "    " + location + "\\\\\n"
        title_content += "    \\vspace{2pt}\n"
    
    title_content += "    \\small\n"
    
    contact_parts = []
    if phone:
        phone_escaped = escape_latex(phone)
        contact_parts.append("\\href{tel:" + phone + "}{\\faPhone~" + phone_escaped + "}")
    if email:
        email_escaped = escape_latex(email)
        contact_parts.append("\\href{mailto:" + email + "}{\\faEnvelope~" + email_escaped + "}")
    
    if contact_parts:
        title_content += "    " + " \\hspace{10pt} ".join(contact_parts) + "\\\\\n"
        title_content += "    \\vspace{2pt}\n"
    
    social_parts = []
    if linkedin:
        # Extract username from URL if full URL provided
        linkedin_display = linkedin.replace('https://www.linkedin.com/in/', '').replace('https://linkedin.com/in/', '').replace('/', '')
        linkedin_display_escaped = escape_latex(linkedin_display)
        # Try \faLinkedinSquare first (as in template), fallback to \faLinkedin if needed
        # Note: May need to ensure fontawesome5 brands is loaded
        social_parts.append("\\href{" + linkedin + "}{\\faLinkedinSquare~linkedin.com/in/" + linkedin_display_escaped + "}")
    if github:
        github_display = github.replace('https://github.com/', '').replace('https://www.github.com/', '').replace('/', '')
        github_display_escaped = escape_latex(github_display)
        social_parts.append("\\href{" + github + "}{\\faGithub~github.com/" + github_display_escaped + "}")
    if website:
        website_display = website.replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
        website_display_escaped = escape_latex(website_display)
        social_parts.append("\\href{" + website + "}{" + website_display_escaped + "}")
    if leetcode:
        leetcode_display = leetcode.replace('https://leetcode.com/', '').replace('https://www.leetcode.com/', '').replace('/', '')
        leetcode_display_escaped = escape_latex(leetcode_display)
        social_parts.append("\\href{" + leetcode + "}{\\textbf{LeetCode:}~leetcode.com/" + leetcode_display_escaped + "}")
    
    if social_parts:
        title_content += "    " + " \\hspace{10pt} ".join(social_parts) + "\\\\\n"
    
    title_content += "    \\vspace{-6pt}\n"
    title_content += "\\end{center}\n"
    
    return title_content

def generate_education_section(educations: List[Dict]) -> str:
    """Generate Education.tex content"""
    if not educations:
        return ""
    
    content = "\\section{EDUCATION} \n{\n"
    
    for i, edu in enumerate(educations):
        if i > 0:
            content += "    \\vspace{-5pt}\n"
        
        content += "    \\resumeSubHeadingListStart\n"
        
        institution = escape_latex(edu.get('institution', ''))
        degree = escape_latex(edu.get('degree', ''))
        start_date = format_date_for_latex(edu.get('start_date', ''))
        end_date = format_date_for_latex(edu.get('end_date')) if edu.get('end_date') else 'Present'
        date_range = f"{start_date} -- {end_date}"
        description = escape_latex(edu.get('description', ''))
        location = ""  # Can be added if location field exists
        
        content += "        \\resumeSubheading\n"
        content += "            {" + institution + "}{" + date_range + "}\n"
        content += "            {" + degree + "}{" + location + "}\n"
        
        if description:
            content += "            \n"
            content += "            \\resumeItemListStart\n"
            # Use string concatenation to avoid f-string brace issues
            content += "                \\resumeItem{\\textbf{Relevant Coursework:} " + description + "}\n"
            content += "            \\resumeItemListEnd\n"
        
        content += "    \\resumeSubHeadingListEnd\n"
    
    content += "}\n"
    
    return content

def generate_technical_skills_section(skills: List[Dict]) -> str:
    """Generate TechnicalSkills.tex content"""
    if not skills:
        return ""
    
    # Group skills by category
    skills_by_category: Dict[str, List[str]] = {}
    for skill in skills:
        category = skill.get('category', 'Other')
        name = escape_latex(skill.get('name', ''))
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(name)
    
    content = "\\section{TECHNICAL SKILLS} {\n"
    content += "    \\begin{itemize}[leftmargin=0.15in, label={}]\n"
    
    for category, skill_names in skills_by_category.items():
        category_display = escape_latex(category)
        skills_list = ", ".join(skill_names)
        # Use string concatenation to avoid f-string brace issues
        content += "        \\item{\\textbf{\\normalsize{" + category_display + ":}} { \\normalsize{" + skills_list + "}}}\n"
        content += "        \\vspace{-0.3cm}\n\n"
    
    content += "    \\end{itemize}\n"
    content += "}\n"
    
    return content

def generate_experience_section(experiences: List[Dict]) -> str:
    """Generate Experience section content"""
    if not experiences:
        return ""
    
    content = "\\section{EXPERIENCE} {\n"
    content += "    \\resumeSubHeadingListStart\n"
    
    for exp in experiences:
        title = escape_latex(exp.get('title', ''))
        company = escape_latex(exp.get('company', ''))
        start_date = format_date_for_latex(exp.get('start_date', ''))
        end_date = format_date_for_latex(exp.get('end_date')) if exp.get('end_date') else 'Present'
        date_range = f"{start_date} -- {end_date}"
        description = escape_latex(exp.get('description', ''))
        technologies = exp.get('technologies', [])
        
        content += "        \\resumeSubheading\n"
        content += "            {" + title + " (" + company + ")}{" + date_range + "}\n"
        content += "            {}{}\n"
        content += "        \\vspace{-15pt}\n"
        content += "        \\resumeItemListStart\n"
        
        # Split description into bullet points if it contains newlines
        desc_lines = description.split('\n') if '\n' in description else [description]
        for line in desc_lines:
            if line.strip():
                # Add technologies mention if available and not already in description
                tech_mention = ""
                if technologies and not any(t.lower() in line.lower() for t in technologies):
                    tech_list = ", ".join([escape_latex(t) for t in technologies])
                    tech_mention = " using \\textbf{" + tech_list + "}"
                content += "            \\resumeItem{" + line.strip() + tech_mention + "}\n"
        
        content += "        \\resumeItemListEnd\n"
    
    content += "    \\resumeSubHeadingListEnd\n"
    content += "}\n"
    
    return content

def generate_projects_section(projects: List[Dict]) -> str:
    """Generate Projects section content"""
    if not projects:
        return ""
    
    content = "\\section{PROJECTS} {\n"
    content += "    \\resumeSubHeadingListStart\n"
    content += "        \\vspace{-6pt} \n"
    
    for i, proj in enumerate(projects):
        if i > 0:
            content += "        \\vspace{-13pt}\n\n"
        
        title = escape_latex(proj.get('title', ''))
        technologies = proj.get('technologies', [])
        tech_str = ", ".join([escape_latex(t) for t in technologies]) if technologies else ""
        description = escape_latex(proj.get('description', ''))
        live_url = proj.get('live_url', '')
        code_url = proj.get('code_url', '')
        
        # Format project heading
        project_title_part = "\\textbf{\\large{\\underline{" + title + "}}}"
        if live_url:
            # Use \faExternalLink as in the template
            project_title_part = "\\href{" + live_url + "}{" + project_title_part + " \\href{" + live_url + "}{\\raisebox{-0.1\\height}\\faExternalLink }}"
        
        if tech_str:
            project_heading = project_title_part + " $|$ \\large{\\underline{" + tech_str + "}}"
        else:
            project_heading = project_title_part
        
        # Use start_date if available (can be int or string)
        start_date = proj.get('start_date', '')
        if start_date:
            if isinstance(start_date, int):
                # If it's an integer (like 202202 for Feb 2022), format it
                date_str = str(start_date)
                if len(date_str) == 6:  # Format: YYYYMM
                    year = date_str[:4]
                    month = int(date_str[4:6])
                    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    date_str = f"{month_names[month]} {year}" if month < len(month_names) else year
            else:
                date_str = format_date_for_latex(str(start_date))
        else:
            date_str = ""
        
        content += "        \\resumeProjectHeading{" + project_heading + "}{" + date_str + "}\n"
        content += "        \\resumeItemListStart\n"
        content += "            \\resumeItem{\\normalsize{" + description + "}}\n"
        content += "        \\resumeItemListEnd\n"
    
    content += "    \\resumeSubHeadingListEnd\n"
    content += "}\n"
    
    return content

def generate_certifications_section(certifications: List[Dict]) -> str:
    """Generate Certifications section content"""
    if not certifications:
        return "% \\section{CERTIFICATIONS}\n\n"
    
    content = "\\section{CERTIFICATIONS}\n\n"
    
    # Format certifications in a grid-like layout
    cert_items = []
    for cert in certifications:
        name = escape_latex(cert.get('name', ''))
        issuer = escape_latex(cert.get('issuer', ''))
        credential_url = cert.get('credential_url', '')
        issue_date = format_date_for_latex(cert.get('issue_date', ''))
        
        cert_text = name + " - " + issuer
        if credential_url:
            cert_text = "\\href{" + credential_url + "}{" + cert_text + "}"
        
        cert_items.append("\\textbullet \\hspace{0.1cm} {" + cert_text + "}")
    
    # Format in rows (2 per row)
    for i in range(0, len(cert_items), 2):
        row = cert_items[i]
        if i + 1 < len(cert_items):
            row += f" \\hspace{{1.6cm}} {cert_items[i + 1]}"
        content += row + "\\\\\n"
    
    return content

def generate_achievements_section(awards: List[Dict]) -> str:
    """Generate Achievements section content"""
    if not awards:
        return ""
    
    content = "\\section{ACHIEVEMENTS}\n{\n"
    content += "    \\resumeItemListStart\n"
    
    for award in awards:
        name = escape_latex(award.get('name', ''))
        issuer = escape_latex(award.get('issuer', ''))
        description = escape_latex(award.get('description', ''))
        
        award_text = "\\textbf{" + name + "}: " + description
        if issuer:
            award_text = "\\textbf{" + name + "} (" + issuer + "): " + description
        
        content += "        \\resumeItem{" + award_text + "}\n"
    
    content += "    \\resumeItemListEnd\n"
    content += "}\n"
    
    return content

def generate_latex_resume(user_data: Dict, experiences: List[Dict], educations: List[Dict],
                          projects: List[Dict], skills: List[Dict], certifications: List[Dict],
                          awards: List[Dict]) -> str:
    """Generate complete LaTeX resume document"""
    
    # Read template files
    template_path = RESUME_TEMPLATE_DIR / "Template.tex"
    methods_path = RESUME_TEMPLATE_DIR / "Methods.tex"
    
    if not RESUME_TEMPLATE_DIR.exists():
        raise FileNotFoundError(f"Resume template directory not found at: {RESUME_TEMPLATE_DIR}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template.tex not found at: {template_path}")
    if not methods_path.exists():
        raise FileNotFoundError(f"Methods.tex not found at: {methods_path}")
    
    template_content = template_path.read_text(encoding='utf-8')
    methods_content = methods_path.read_text(encoding='utf-8')
    
    # Remove or comment out problematic inputs that may not be available
    # These are typically provided by LaTeX distributions but may not be in the expected location
    template_content = template_content.replace('\\input{glyphtounicode}', '% \\input{glyphtounicode}  % Commented out - may not be available')
    template_content = template_content.replace('\\input glyphtounicode.tex', '% \\input glyphtounicode.tex  % Commented out - may not be available')
    template_content = template_content.replace('\\input glyphtounicode-cmr.tex', '% \\input glyphtounicode-cmr.tex  % Commented out - may not be available')
    
    # Generate sections
    title_content = generate_title_section(user_data)
    education_content = generate_education_section(educations)
    skills_content = generate_technical_skills_section(skills)
    experience_content = generate_experience_section(experiences)
    projects_content = generate_projects_section(projects)
    certifications_content = generate_certifications_section(certifications)
    achievements_content = generate_achievements_section(awards)
    
    # Build complete LaTeX document
    latex_doc = "\\documentclass[letterpaper,11pt]{article}\n\n"
    latex_doc += "\\usepackage{latexsym}\n"
    latex_doc += "\\usepackage[empty]{fullpage}\n"
    latex_doc += "\\usepackage{titlesec}\n"
    latex_doc += "\\usepackage{marvosym}\n"
    latex_doc += "\\usepackage[usenames,dvipsnames]{color}\n"
    latex_doc += "\\usepackage{verbatim}\n"
    latex_doc += "\\usepackage{enumitem}\n"
    latex_doc += "\\usepackage[hidelinks]{hyperref}\n"
    latex_doc += "\\usepackage[english]{babel}\n"
    latex_doc += "\\usepackage{tabularx}\n"
    latex_doc += "\\usepackage{fontawesome5}\n"
    latex_doc += "\\usepackage{multicol}\n"
    latex_doc += "\\usepackage{graphicx}\n"
    latex_doc += "\\usepackage{tikz}\n\n"
    
    # Add template content (which includes package requirements)
    # Note: template_content may include \RequirePackage commands
    latex_doc += template_content + "\n"
    latex_doc += methods_content + "\n\n"
    
    latex_doc += "\\begin{document}\n"
    latex_doc += "	\\vspace{-15pt}\n"
    latex_doc += title_content + "\n"
    latex_doc += "	\\vspace{-10pt}\n\n"
    
    latex_doc += skills_content + "\n"
    latex_doc += "	\\vspace{-15pt}\n\n"
    
    latex_doc += experience_content + "\n"
    latex_doc += "	\\vspace{-10pt}\n\n"
    
    latex_doc += education_content + "\n"
    latex_doc += "	\\vspace{-10pt}\n\n"
    
    latex_doc += projects_content + "\n"
    latex_doc += "	\\vspace{-10pt}\n\n"
    
    if certifications_content.strip() and not certifications_content.startswith("%"):
        latex_doc += certifications_content + "\n"
        latex_doc += "	\\vspace{-10pt}\n\n"
    
    if achievements_content.strip():
        latex_doc += achievements_content + "\n"
    
    latex_doc += "\\end{document}\n"
    
    return latex_doc

def compile_latex_to_pdf(latex_content: str, output_dir: Path) -> Path:
    """Compile LaTeX content to PDF using pdflatex"""
    # Write LaTeX file
    tex_file = output_dir / "resume.tex"
    tex_file.write_text(latex_content, encoding='utf-8')
    
    # Note: Template.tex and Methods.tex are now included inline in latex_content
    # so we don't need to copy them separately
    
    # Compile LaTeX to PDF
    try:
        # Check if pdflatex is available
        pdflatex_check = subprocess.run(['which', 'pdflatex'], capture_output=True, text=True)
        if pdflatex_check.returncode != 0:
            raise RuntimeError("pdflatex not found. Please install LaTeX (e.g., texlive-full or MacTeX)")
        
        # Run pdflatex twice for proper references
        pdf_file = output_dir / "resume.pdf"
        for run_num in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(output_dir), str(tex_file)],
                capture_output=True,
                text=True,
                cwd=str(output_dir),
                timeout=60,  # 60 second timeout
                encoding='utf-8',
                errors='replace'  # Replace invalid UTF-8 characters instead of failing
            )
            
            # Check if PDF was generated (even if returncode is non-zero)
            # LaTeX often returns non-zero on warnings but still generates PDF
            if pdf_file.exists():
                # PDF was generated successfully, continue even if there were warnings
                break
            elif result.returncode != 0:
                # Only fail if PDF wasn't generated AND there was an error
                error_msg = f"LaTeX compilation failed (run {run_num + 1}):\n"
                error_msg += f"Return code: {result.returncode}\n"
                # Get last part of output for debugging
                stdout_tail = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
                stderr_tail = result.stderr[-3000:] if len(result.stderr) > 3000 else result.stderr
                error_msg += f"STDOUT (last 3000 chars):\n{stdout_tail}\n"
                error_msg += f"STDERR (last 3000 chars):\n{stderr_tail}\n"
                raise RuntimeError(error_msg)
        
        # Final check that PDF exists
        if not pdf_file.exists():
            raise FileNotFoundError("PDF file was not generated after compilation")
        
        return pdf_file
    except subprocess.TimeoutExpired:
        raise RuntimeError("LaTeX compilation timed out after 60 seconds")
    except FileNotFoundError as e:
        if "pdflatex" in str(e):
            raise RuntimeError("pdflatex not found. Please install LaTeX (e.g., texlive-full or MacTeX)")
        raise
