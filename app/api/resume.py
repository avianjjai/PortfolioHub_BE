from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from app.models.user import User
from app.models.experience import Experience
from app.models.education import Education
from app.models.project import Project
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.award import Award
from datetime import datetime
import tempfile
from pathlib import Path
from app.utils.latex_compiler import compile_latex_to_pdf
from app.ResumeGenerator.templates.resume import Resume
from beanie import PydanticObjectId

router = APIRouter()

@router.get('/latex')
async def get_resume_latex(user_id: PydanticObjectId = Query(..., description="User ID for the resume to generate")):
    """
    Generate and download resume PDF using LaTeX template for the specified user.
    This endpoint is public and does not require authentication.
    Anyone can download any user's resume by providing their user_id.
    """
    try:
        # Get user by ID
        user = await User.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user data
        user_data = user.model_dump(exclude={"hashed_password"})
        
        # Get all related data
        
        experiences = await Experience.find(Experience.user_id == user_id).to_list()
        experiences.sort(key=lambda x: x.end_date if x.end_date else x.start_date, reverse=True)
        
        educations = await Education.find(Education.user_id == user_id).to_list()
        educations.sort(key=lambda x: x.end_date if x.end_date else x.start_date, reverse=True)
        
        projects = await Project.find(Project.user_id == user_id).to_list()
        projects.sort(key=lambda x: x.end_date if x.end_date else x.start_date, reverse=True)
        
        skills = await Skill.find(Skill.user_id == user_id).to_list()
        
        certifications = await Certification.find(Certification.user_id == user_id).to_list()
        
        awards = await Award.find(Award.user_id == user_id).to_list()
        
        # Convert to dict format and format dates
        def format_date(date_obj):
            if date_obj is None:
                return None
            if isinstance(date_obj, datetime):
                return date_obj.strftime('%Y-%m-%d')
            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%Y-%m-%d')
            return str(date_obj)
        
        experiences_data = []
        for exp in experiences:
            exp_dict = exp.model_dump()
            exp_dict['start_date'] = format_date(exp.start_date)
            exp_dict['end_date'] = format_date(exp.end_date) if exp.end_date else None
            experiences_data.append(exp_dict)
        
        educations_data = []
        for edu in educations:
            edu_dict = edu.model_dump()
            edu_dict['start_date'] = format_date(edu.start_date)
            edu_dict['end_date'] = format_date(edu.end_date) if edu.end_date else None
            educations_data.append(edu_dict)
        
        projects_data = []
        for proj in projects:
            proj_dict = proj.model_dump()
            # Format dates the same way as experience (convert epoch to date string)
            proj_dict['start_date'] = format_date(proj.start_date)
            proj_dict['end_date'] = format_date(proj.end_date) if proj.end_date else None
            projects_data.append(proj_dict)
        
        skills_data = [skill.model_dump() for skill in skills]
        certifications_data = [cert.model_dump() for cert in certifications]
        
        awards_data = []
        for award in awards:
            award_dict = award.model_dump()
            # Format issue_date the same way as other dates
            award_dict['issue_date'] = format_date(award.issue_date) if award.issue_date else None
            awards_data.append(award_dict)

        latex_content = Resume().generate_resume(
            user_data=user_data,
            experiences=experiences_data,
            educations=educations_data,
            projects=projects_data,
            skills=skills_data,
            certifications=certifications_data,
            awards=awards_data
        )
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pdf_file = compile_latex_to_pdf(latex_content, temp_path)
            
            # Read PDF bytes
            pdf_bytes = pdf_file.read_bytes()
            
            # Generate filename
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            filename = f"{first_name}_{last_name}_Resume.pdf".strip() or "Resume.pdf"
            filename = filename.replace(' ', '_')
            
            # Return PDF as response
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"LaTeX template files not found: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"LaTeX compilation error: {str(e)}")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        # Log full error for debugging
        print(f"Resume generation error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")
