"""
Resume Parser & Job Matcher API

A FastAPI application that parses resumes and matches them against job descriptions,
providing similarity scores and recommendations for job seekers.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from typing import Dict, Any

from resume_parser import ResumeParser
from job_matcher import JobMatcher

app = FastAPI(
    title="Resume Parser & Job Matcher",
    description="Parse resumes and match them against job descriptions with AI-powered analysis",
    version="1.0.0"
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize components
resume_parser = ResumeParser()
job_matcher = JobMatcher()

class MatchRequest(BaseModel):
    """Request model for job matching endpoint."""
    resume_data: Dict[str, Any]
    job_description: str

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Web interface not found")

@app.post("/upload-resume")
async def upload_resume(resume: UploadFile = File(...)):
    """
    Process uploaded resume file and extract structured data.
    
    Supports PDF, DOC, and DOCX formats.
    Returns extracted information including skills, experience, and education.
    """
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = os.path.splitext(resume.filename.lower())[1]
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload PDF, DOC, or DOCX files."
        )
    
    content = await resume.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")
    
    try:
        if file_ext == '.pdf':
            resume_data = resume_parser.parse_pdf(content)
        else:
            resume_data = resume_parser.parse_docx(content)
        
        return {"status": "success", "data": resume_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.post("/match-jobs")
async def match_jobs(match_request: MatchRequest):
    """
    Calculate match score between resume and job description.
    
    Analyzes skills, experience, and education compatibility.
    Returns detailed scoring breakdown and improvement recommendations.
    """
    if not match_request.resume_data:
        raise HTTPException(status_code=400, detail="Resume data is required")
    
    if not match_request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    
    try:
        job_data = job_matcher.parse_job_description(match_request.job_description)
        match_result = job_matcher.calculate_match(match_request.resume_data, job_data)
        
        # Generate personalized recommendations based on score
        score = match_result['overall_score']
        if score < 50:
            recommendations = [
                "Focus on developing the missing technical skills",
                "Consider relevant certifications or courses",
                "Highlight transferable skills from other experiences"
            ]
        elif score < 70:
            recommendations = [
                "Strong candidate profile with room for improvement",
                "Emphasize relevant projects and achievements",
                "Tailor your resume to better match job requirements"
            ]
        else:
            recommendations = [
                "Excellent match for this position!",
                "Apply with confidence",
                "Highlight your strongest matching skills in your application"
            ]
        
        match_result['recommendations'] = recommendations
        return {"status": "success", "match": match_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching jobs: {str(e)}")

@app.get("/sample-jobs")
async def get_sample_jobs():
    """
    Retrieve sample job descriptions for testing and demonstration.
    
    Returns a collection of pre-defined job postings across different roles.
    """
    try:
        return {"status": "success", "jobs": job_matcher.get_sample_jobs()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sample jobs: {str(e)}")

@app.get("/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "service": "Resume Parser & Job Matcher"}

if __name__ == "__main__":
    print("🚀 Starting Resume Parser & Job Matcher...")
    print("📍 Server available at: http://127.0.0.1:8000")
    print("📖 API documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)