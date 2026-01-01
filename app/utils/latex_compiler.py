"""Utility functions for compiling LaTeX to PDF"""
import subprocess
from pathlib import Path
from datetime import timezone


def compile_latex_to_pdf(latex_content: str, output_dir: Path) -> Path:
    """Compile LaTeX content to PDF using pdflatex"""
    # Write LaTeX file
    tex_file = output_dir / "resume.tex"
    tex_file.write_text(latex_content, encoding='utf-8')
    
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
