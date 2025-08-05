import numpy as np
from models.job_matcher import JobMatcher
from utils.text_processing import TextProcessor
import config

class ScoringEngine:
    """Resume scoring engine that evaluates resumes comprehensively"""
    
    def __init__(self):
        self.job_matcher = JobMatcher()
        self.text_processor = TextProcessor()
    
    def calculate_overall_score(self, parsed_resume, resume_text, job_description=None):
        """Calculate comprehensive resume score"""
        scores = {}
        
        # 1. Completeness Score (30% weight)
        scores['completeness'] = self.calculate_completeness_score(parsed_resume)
        
        # 2. Content Quality Score (25% weight)
        scores['content_quality'] = self.calculate_content_quality_score(resume_text)
        
        # 3. Skills Relevance Score (20% weight)
        scores['skills_relevance'] = self.calculate_skills_relevance_score(parsed_resume)
        
        # 4. Experience Score (15% weight)
        scores['experience'] = self.calculate_experience_score(parsed_resume)
        
        # 5. Job Match Score (10% weight) - only if job description provided
        if job_description:
            match_result = self.job_matcher.calculate_similarity_score(resume_text, job_description)
            scores['job_match'] = match_result['overall_score'] / 100  # Convert back to 0-1 scale
        else:
            scores['job_match'] = 0.0
        
        # Calculate weighted overall score
        weights = {
            'completeness': 0.30,
            'content_quality': 0.25,
            'skills_relevance': 0.20,
            'experience': 0.15,
            'job_match': 0.10
        }
        
        overall_score = sum(scores[category] * weights[category] for category in scores)
        
        return {
            'overall_score': round(overall_score * 100, 2),
            'category_scores': {k: round(v * 100, 2) for k, v in scores.items()},
            'grade': self.get_score_grade(overall_score * 100),
            'feedback': self.generate_feedback(scores, parsed_resume)
        }
    
    def calculate_completeness_score(self, parsed_resume):
        """Calculate completeness score based on resume sections"""
        required_sections = {
            'name': parsed_resume.get('name', '') != '',
            'contact': bool(parsed_resume.get('email') or parsed_resume.get('phone')),
            'skills': len(parsed_resume.get('skills', [])) > 0,
            'education': len(parsed_resume.get('education', [])) > 0,
            'experience': (parsed_resume.get('experience_years', 0) > 0 or 
                          len(parsed_resume.get('companies', [])) > 0)
        }
        
        optional_sections = {
            'projects': 'projects' in parsed_resume.get('sections', {}),
            'certifications': 'certifications' in parsed_resume.get('sections', {}),
            'summary': any(section in parsed_resume.get('sections', {}) 
                          for section in ['summary', 'objective'])
        }
        
        # Required sections: 70% weight
        required_score = sum(required_sections.values()) / len(required_sections) * 0.7
        
        # Optional sections: 30% weight
        optional_score = sum(optional_sections.values()) / len(optional_sections) * 0.3
        
        return required_score + optional_score
    
    def calculate_content_quality_score(self, resume_text):
        """Calculate content quality based on text analysis"""
        if not resume_text:
            return 0.0
        
        stats = self.text_processor.get_text_statistics(resume_text)
        
        # Scoring criteria
        word_count = stats.get('word_count', 0)
        sentence_count = stats.get('sentence_count', 0)
        avg_words_per_sentence = stats.get('avg_words_per_sentence', 0)
        unique_words = stats.get('unique_words', 0)
        
        scores = []
        
        # Word count score (ideal range: 300-800 words)
        if 300 <= word_count <= 800:
            word_score = 1.0
        elif 200 <= word_count < 300 or 800 < word_count <= 1000:
            word_score = 0.8
        elif 100 <= word_count < 200 or 1000 < word_count <= 1200:
            word_score = 0.6
        else:
            word_score = 0.4
        scores.append(word_score)
        
        # Sentence structure score (ideal: 10-25 words per sentence)
        if 10 <= avg_words_per_sentence <= 25:
            sentence_score = 1.0
        elif 8 <= avg_words_per_sentence < 10 or 25 < avg_words_per_sentence <= 30:
            sentence_score = 0.8
        else:
            sentence_score = 0.6
        scores.append(sentence_score)
        
        # Vocabulary diversity score
        if word_count > 0:
            diversity_ratio = unique_words / word_count
            if diversity_ratio >= 0.5:
                diversity_score = 1.0
            elif diversity_ratio >= 0.4:
                diversity_score = 0.8
            elif diversity_ratio >= 0.3:
                diversity_score = 0.6
            else:
                diversity_score = 0.4
        else:
            diversity_score = 0.0
        scores.append(diversity_score)
        
        return sum(scores) / len(scores)
    
    def calculate_skills_relevance_score(self, parsed_resume):
        """Calculate skills relevance and diversity score"""
        skills = parsed_resume.get('skills', [])
        
        if not skills:
            return 0.0
        
        technical_skills = []
        soft_skills = []
        
        # Categorize skills
        for skill in skills:
            skill_lower = skill.lower()
            if any(tech_skill.lower() in skill_lower for tech_skill in config.TECHNICAL_SKILLS):
                technical_skills.append(skill)
            elif any(soft_skill.lower() in skill_lower for soft_skill in config.SOFT_SKILLS):
                soft_skills.append(skill)
        
        # Scoring criteria
        total_skills = len(skills)
        tech_skills_count = len(technical_skills)
        soft_skills_count = len(soft_skills)
        
        scores = []
        
        # Skills quantity score (ideal: 8-15 skills)
        if 8 <= total_skills <= 15:
            quantity_score = 1.0
        elif 5 <= total_skills < 8 or 15 < total_skills <= 20:
            quantity_score = 0.8
        elif 3 <= total_skills < 5 or 20 < total_skills <= 25:
            quantity_score = 0.6
        else:
            quantity_score = 0.4
        scores.append(quantity_score)
        
        # Technical skills score
        if tech_skills_count >= 5:
            tech_score = 1.0
        elif tech_skills_count >= 3:
            tech_score = 0.8
        elif tech_skills_count >= 1:
            tech_score = 0.6
        else:
            tech_score = 0.2
        scores.append(tech_score)
        
        # Balance score (mix of technical and soft skills)
        if tech_skills_count > 0 and soft_skills_count > 0:
            balance_score = 1.0
        elif tech_skills_count > 0 or soft_skills_count > 0:
            balance_score = 0.7
        else:
            balance_score = 0.3
        scores.append(balance_score)
        
        return sum(scores) / len(scores)
    
    def calculate_experience_score(self, parsed_resume):
        """Calculate experience score"""
        experience_years = parsed_resume.get('experience_years', 0)
        companies = parsed_resume.get('companies', [])
        designations = parsed_resume.get('designations', [])
        
        scores = []
        
        # Years of experience score
        if experience_years >= 5:
            exp_score = 1.0
        elif experience_years >= 3:
            exp_score = 0.8
        elif experience_years >= 1:
            exp_score = 0.6
        elif experience_years > 0:
            exp_score = 0.4
        else:
            exp_score = 0.0
        scores.append(exp_score)
        
        # Companies mentioned score
        if len(companies) >= 3:
            company_score = 1.0
        elif len(companies) >= 2:
            company_score = 0.8
        elif len(companies) >= 1:
            company_score = 0.6
        else:
            company_score = 0.2
        scores.append(company_score)
        
        # Career progression score (based on designations)
        if len(designations) >= 2:
            progression_score = 1.0
        elif len(designations) >= 1:
            progression_score = 0.7
        else:
            progression_score = 0.3
        scores.append(progression_score)
        
        return sum(scores) / len(scores)
    
    def get_score_grade(self, score):
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'D'
    
    def generate_feedback(self, scores, parsed_resume):
        """Generate detailed feedback based on scores"""
        feedback = []
        
        # Completeness feedback
        completeness_score = scores['completeness']
        if completeness_score < 0.7:
            missing_sections = []
            if not parsed_resume.get('name'):
                missing_sections.append("name")
            if not (parsed_resume.get('email') or parsed_resume.get('phone')):
                missing_sections.append("contact information")
            if not parsed_resume.get('skills'):
                missing_sections.append("skills section")
            if not parsed_resume.get('education'):
                missing_sections.append("education details")
            
            if missing_sections:
                feedback.append(f"📝 **Missing Information**: Add {', '.join(missing_sections)}")
        
        # Content quality feedback
        content_score = scores['content_quality']
        if content_score < 0.6:
            feedback.append("📄 **Improve Content**: Resume may be too short/long or lack detail")
        
        # Skills feedback
        skills_score = scores['skills_relevance']
        if skills_score < 0.6:
            skills_count = len(parsed_resume.get('skills', []))
            if skills_count < 5:
                feedback.append("🎯 **Add More Skills**: Include relevant technical and soft skills")
            elif skills_count > 20:
                feedback.append("🎯 **Optimize Skills**: Focus on most relevant skills (8-15 recommended)")
        
        # Experience feedback
        exp_score = scores['experience']
        if exp_score < 0.5:
            if parsed_resume.get('experience_years', 0) == 0:
                feedback.append("💼 **Add Experience**: Include internships, projects, or volunteer work")
            else:
                feedback.append("💼 **Enhance Experience**: Add more details about roles and achievements")
        
        # Job match feedback
        job_match_score = scores.get('job_match', 0)
        if job_match_score > 0 and job_match_score < 0.6:
            feedback.append("🎯 **Improve Job Match**: Tailor resume to better match job requirements")
        
        # Positive feedback for high scores
        if scores['completeness'] >= 0.8:
            feedback.append("✅ **Complete Profile**: Well-structured resume with all essential sections")
        
        if scores['skills_relevance'] >= 0.8:
            feedback.append("🌟 **Strong Skills Profile**: Good mix of relevant technical and soft skills")
        
        return feedback
    
    def get_improvement_suggestions(self, parsed_resume, resume_text):
        """Get specific improvement suggestions"""
        suggestions = []
        
        # Check for quantifiable achievements
        if not any(char.isdigit() for char in resume_text):
            suggestions.append("📊 **Add Numbers**: Include metrics, percentages, or quantities to showcase impact")
        
        # Check for action verbs
        action_verbs = ['achieved', 'developed', 'managed', 'led', 'created', 'improved', 'increased']
        if not any(verb in resume_text.lower() for verb in action_verbs):
            suggestions.append("⚡ **Use Action Verbs**: Start bullet points with strong action verbs")
        
        # Check resume length
        word_count = len(resume_text.split())
        if word_count < 200:
            suggestions.append("📝 **Expand Content**: Add more details about your experience and achievements")
        elif word_count > 1000:
            suggestions.append("✂️ **Concise Writing**: Consider reducing content to focus on most relevant information")
        
        # Check for contact information
        if not parsed_resume.get('email'):
            suggestions.append("📧 **Add Email**: Include a professional email address")
        
        if not parsed_resume.get('phone'):
            suggestions.append("📱 **Add Phone**: Include your phone number for contact")
        
        return suggestions