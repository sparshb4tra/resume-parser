import re
from typing import List, Dict, Any

class JobMatcher:
    def __init__(self):
        # Matching weights
        self.weights = {
            'skills': 0.50,
            'experience': 0.30,
            'education': 0.20
        }
        
        # Comprehensive skill list for better matching
        self.skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'html', 'css',
            'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'spring', 'laravel', 'bootstrap', 'tailwind', 'sql', 'mysql', 'postgresql',
            'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle', 'cassandra',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'git', 'github', 'gitlab', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
            'pytorch', 'keras', 'spark', 'hadoop', 'tableau', 'powerbi', 'excel',
            'linux', 'bash', 'agile', 'scrum', 'devops', 'ci/cd', 'restful', 'api',
            'microservices', 'machine learning', 'data analysis', 'data science'
        ]
        
        # Sample job descriptions for testing
        self.sample_jobs = [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp",
                "description": """
We are seeking a Senior Software Engineer to join our dynamic team. 

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python, JavaScript, and SQL
- Experience with React, Node.js, and RESTful APIs
- Knowledge of cloud platforms (AWS/Azure)
- Bachelor's degree in Computer Science or related field
- Experience with agile development methodologies

Responsibilities:
- Design and develop scalable web applications
- Collaborate with cross-functional teams
- Mentor junior developers
- Participate in code reviews and technical discussions

Preferred:
- Experience with Docker and Kubernetes
- Knowledge of machine learning frameworks
- Experience with microservices architecture
                """
            },
            {
                "title": "Data Scientist",
                "company": "DataTech Inc",
                "description": """
Join our data science team to drive insights and build predictive models.

Requirements:
- Master's degree in Data Science, Statistics, or related field
- 3+ years of experience in data analysis and machine learning
- Proficiency in Python, R, and SQL
- Experience with pandas, numpy, scikit-learn, TensorFlow
- Strong statistical analysis skills
- Experience with data visualization tools (Tableau, Power BI)

Responsibilities:
- Develop and deploy machine learning models
- Analyze large datasets to extract actionable insights
- Create data visualizations and reports
- Collaborate with business stakeholders

Preferred:
- PhD in quantitative field
- Experience with big data technologies (Spark, Hadoop)
- Knowledge of deep learning frameworks
                """
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "description": """
Looking for a versatile Full Stack Developer to build amazing products.

Requirements:
- 3+ years of full-stack development experience
- Frontend: React, Vue.js, or Angular
- Backend: Node.js, Express, or Django
- Database experience: MongoDB, PostgreSQL
- Experience with Git version control
- Bachelor's degree preferred

Responsibilities:
- Build responsive web applications
- Design and implement APIs
- Work with designers and product managers
- Optimize application performance

Preferred:
- Experience with TypeScript
- Knowledge of DevOps practices
- Mobile development experience
- Experience with GraphQL
                """
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudSystems",
                "description": """
Seeking a DevOps Engineer to manage our cloud infrastructure and CI/CD pipelines.

Requirements:
- 4+ years of DevOps/Infrastructure experience
- Strong experience with AWS or Azure
- Proficiency in Docker and Kubernetes
- Experience with Infrastructure as Code (Terraform, CloudFormation)
- Knowledge of CI/CD tools (Jenkins, GitLab CI)
- Scripting skills in Python or Bash

Responsibilities:
- Manage cloud infrastructure and deployments
- Build and maintain CI/CD pipelines
- Monitor system performance and reliability
- Implement security best practices

Preferred:
- Certifications in AWS/Azure
- Experience with monitoring tools (Prometheus, Grafana)
- Knowledge of service mesh technologies
                """
            },
            {
                "title": "Product Manager",
                "company": "InnovateTech",
                "description": """
We're looking for a Product Manager to drive product strategy and execution.

Requirements:
- 5+ years of product management experience
- MBA or equivalent experience
- Strong analytical and problem-solving skills
- Experience with agile development methodologies
- Excellent communication and leadership skills
- Data-driven decision making

Responsibilities:
- Define product roadmap and strategy
- Work with engineering and design teams
- Conduct market research and competitive analysis
- Manage product launches and go-to-market strategy

Preferred:
- Technical background in software development
- Experience with B2B SaaS products
- Knowledge of SQL and data analysis tools
                """
            }
        ]

    def parse_job_description(self, job_text: str) -> Dict[str, Any]:
        """Parse job description and extract structured information"""
        job_data = {
            "title": self._extract_job_title(job_text),
            "company": self._extract_company(job_text),
            "required_skills": self._extract_skills(job_text, section_type="required"),
            "preferred_skills": self._extract_skills(job_text, section_type="preferred"),
            "experience_required": self._extract_experience_requirement(job_text),
            "education_required": self._extract_education_requirement(job_text),
            "responsibilities": self._extract_responsibilities(job_text),
            "raw_text": job_text
        }
        
        return job_data

    def calculate_match(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall match score between resume and job"""
        
        # Calculate individual scores
        skill_score = self._calculate_skill_score(resume_data, job_data)
        education_score = self._calculate_education_score(resume_data, job_data)
        experience_score = self._calculate_experience_score(resume_data, job_data)
        
        # Calculate weighted overall score
        overall_score = (
            skill_score * self.weights['skills'] +
            education_score * self.weights['education'] +
            experience_score * self.weights['experience']
        )
        
        # Generate skill matches and missing skills
        skill_matches = self._get_skill_matches(resume_data, job_data)
        missing_skills = self._get_missing_skills(resume_data, job_data)
        
        return {
            "overall_score": round(overall_score * 100, 1),
            "skill_score": round(skill_score * 100, 1),
            "experience_score": round(experience_score * 100, 1),
            "education_score": round(education_score * 100, 1),
            "matched_skills": skill_matches,
            "missing_skills": missing_skills,
            "breakdown": {
                "Technical Skills": round(skill_score * 100, 1),
                "Education": round(education_score * 100, 1),
                "Experience": round(experience_score * 100, 1)
            }
        }

    def _calculate_skill_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate skill matching score"""
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        required_skills = set(skill.lower() for skill in job_data.get('required_skills', []))
        
        if not required_skills:
            return 0.7
        
        matches = len(resume_skills & required_skills)
        return min(matches / len(required_skills), 1.0)


    def _calculate_education_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate education matching score"""
        education = resume_data.get('education', [])
        if not education:
            return 0.5
        return 0.8

    def _calculate_experience_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate experience matching score"""
        experience = resume_data.get('experience', [])
        if not experience:
            return 0.3
        return min(len(experience) / 3.0, 1.0)

    def _get_skill_matches(self, resume_data: Dict, job_data: Dict) -> List[Dict]:
        """Get skill matches"""
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        required_skills = set(skill.lower() for skill in job_data.get('required_skills', []))
        
        matches = []
        for skill in resume_skills & required_skills:
            matches.append({
                "skill": skill.title(),
                "match_type": "exact",
                "confidence": 1.0
            })
        
        return matches

    def _get_missing_skills(self, resume_data: Dict, job_data: Dict) -> List[str]:
        """Get missing skills"""
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        required_skills = set(skill.lower() for skill in job_data.get('required_skills', []))
        
        missing = required_skills - resume_skills
        return [skill.title() for skill in missing]

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from job description"""
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if 5 < len(line) < 100:
                # Look for common job title patterns
                if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator']):
                    return line
        return "Unknown Position"

    def _extract_company(self, text: str) -> str:
        """Extract company name from job description"""
        lines = text.strip().split('\n')
        for line in lines[:5]:
            if any(word in line.lower() for word in ['company', 'corp', 'inc', 'ltd', 'llc']):
                return line.strip()
        return ""

    def _extract_skills(self, text: str, section_type: str = "all") -> List[str]:
        """Extract skills from job description"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        return list(dict.fromkeys(found_skills))

    def _extract_experience_requirement(self, text: str) -> str:
        """Extract experience requirements"""
        if 'year' in text.lower():
            return "experience mentioned"
        return ""

    def _extract_education_requirement(self, text: str) -> str:
        """Extract education requirements"""
        if any(word in text.lower() for word in ['degree', 'bachelor', 'master', 'phd']):
            return "degree mentioned"
        return ""

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        return ["responsibilities listed in description"]

    def get_sample_jobs(self) -> List[Dict[str, str]]:
        """Return sample job descriptions for testing"""
        return [{"title": job["title"], "company": job["company"], "description": job["description"]} 
                for job in self.sample_jobs]    