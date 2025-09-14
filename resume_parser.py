"""
Resume Parser Module

Extracts structured information from PDF and DOCX resume files including
personal details, skills, experience, education, and achievements.
"""

import re
import io
import pdfplumber
from docx import Document
from typing import List, Dict, Any


class ResumeParser:
    """
    Parses resume files and extracts structured information.
    
    Supports PDF and DOCX formats and extracts:
    - Personal information (name, email, phone)
    - Technical skills
    - Work experience
    - Education
    - Achievements and certifications
    """
    
    def __init__(self):
        """Initialize parser with comprehensive skill database."""
        self.all_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'html', 'css',
            
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'fastapi', 
            'spring', 'laravel', 'bootstrap', 'tailwind',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 
            'oracle', 'cassandra', 'dynamodb',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 
            'git', 'github', 'gitlab', 'ci/cd',
            
            # Data Science & Analytics
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 
            'spark', 'hadoop', 'tableau', 'powerbi', 'excel',
            
            # Tools & Systems
            'linux', 'bash', 'vim', 'vscode', 'intellij', 'jira', 'confluence', 
            'slack', 'postman', 'figma', 'photoshop'
        ]

    def parse_pdf(self, content: bytes) -> Dict[str, Any]:
        """
        Extract and parse text content from PDF resume.
        
        Args:
            content: PDF file content as bytes
            
        Returns:
            Structured resume data dictionary
        """
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return self._parse_text(text)
        except Exception as e:
            raise Exception(f"Failed to parse PDF resume: {str(e)}")

    def parse_docx(self, content: bytes) -> Dict[str, Any]:
        """
        Extract and parse text content from DOCX resume.
        
        Args:
            content: DOCX file content as bytes
            
        Returns:
            Structured resume data dictionary
        """
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            
            return self._parse_text(text)
        except Exception as e:
            raise Exception(f"Failed to parse DOCX resume: {str(e)}")

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse raw resume text and extract structured information.
        
        Args:
            text: Raw text content from resume
            
        Returns:
            Dictionary containing extracted resume information
        """
        if not text.strip():
            raise ValueError("Resume text is empty")
            
        resume_data = {
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "achievements": self._extract_achievements(text),
            "certifications": self._extract_certifications(text),
            "raw_text": text[:1000] + "..." if len(text) > 1000 else text  # Truncate for storage
        }
        
        return resume_data

    def _extract_name(self, text: str) -> str:
        """Extract person's name from resume"""
        lines = text.strip().split('\n')
        
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                # Simple heuristic: if line has 2-4 words and no special chars
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.isalpha() for word in words):
                    return line
        
        return "Unknown"

    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890 or 1234567890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1-123-456-7890
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return ""

    def _extract_skills(self, text: str) -> List[str]:
        text_lower = text.lower()
        found = []
        
        for skill in self.all_skills:
            if skill.lower() in text_lower:
                found.append(skill.title())
        
        return list(dict.fromkeys(found))



    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience"""
        experience = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
                if len(line.strip()) > 10:
                    experience.append({
                        "title": line.strip()[:100],
                        "company": "",
                        "duration": "",
                        "description": line[:200]
                    })
                if len(experience) >= 3:
                    break
        
        return experience

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['bachelor', 'master', 'phd', 'degree', 'university', 'college']):
                education.append({
                    "degree": line.strip()[:100],
                    "institution": "",
                    "year": ""
                })
                if len(education) >= 2:
                    break
        
        return education

    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements"""
        achievements = []
        lines = text.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['award', 'achievement', 'accomplished', 'led', 'increased', 'reduced']):
                if len(line.strip()) > 20:
                    achievements.append(line.strip()[:200])
                if len(achievements) >= 3:
                    break
        
        return achievements

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        lines = text.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['certified', 'certification', 'certificate']):
                if len(line.strip()) > 5:
                    certifications.append(line.strip()[:100])
                if len(certifications) >= 3:
                    break
        
        return certifications