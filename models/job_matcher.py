import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from utils.text_processing import TextProcessor
import config
import re

class JobMatcher:
    """Job matching algorithms to compare resumes with job descriptions"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.vectorizer = TfidfVectorizer(
            max_features=config.MAX_FEATURES_TFIDF,
            stop_words='english',
            ngram_range=(1, 2)  # Include both unigrams and bigrams
        )
    
    def calculate_similarity_score(self, resume_text, job_description):
        """Calculate similarity score between resume and job description using multiple methods"""
        scores = {}
        
        # Preprocess texts
        resume_processed = self.text_processor.preprocess_for_similarity(resume_text)
        job_processed = self.text_processor.preprocess_for_similarity(job_description)
        
        if not resume_processed or not job_processed:
            return {'overall_score': 0.0, 'method_scores': scores}
        
        # Method 1: TF-IDF + Cosine Similarity
        scores['tfidf_cosine'] = self.tfidf_cosine_similarity(resume_processed, job_processed)
        
        # Method 2: Keyword Matching
        scores['keyword_match'] = self.keyword_matching_score(resume_text, job_description)
        
        # Method 3: Skills Matching
        scores['skills_match'] = self.skills_matching_score(resume_text, job_description)
        
        # Method 4: Experience Matching
        scores['experience_match'] = self.experience_matching_score(resume_text, job_description)
        
        # Calculate weighted overall score
        weights = {
            'tfidf_cosine': 0.4,
            'keyword_match': 0.2,
            'skills_match': 0.3,
            'experience_match': 0.1
        }
        
        overall_score = sum(scores[method] * weights[method] for method in scores)
        
        return {
            'overall_score': round(overall_score * 100, 2),  # Convert to percentage
            'method_scores': {k: round(v * 100, 2) for k, v in scores.items()}
        }
    
    def tfidf_cosine_similarity(self, text1, text2):
        """Calculate TF-IDF cosine similarity between two texts"""
        try:
            documents = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return cosine_sim[0][0]
        except Exception as e:
            print(f"Error in TF-IDF cosine similarity: {e}")
            return 0.0
    
    def keyword_matching_score(self, resume_text, job_description):
        """Calculate keyword matching score"""
        try:
            # Extract keywords from job description
            job_keywords = self.extract_important_keywords(job_description)
            
            if not job_keywords:
                return 0.0
            
            resume_lower = resume_text.lower()
            matched_keywords = 0
            
            for keyword in job_keywords:
                if keyword.lower() in resume_lower:
                    matched_keywords += 1
            
            return matched_keywords / len(job_keywords) if job_keywords else 0.0
            
        except Exception as e:
            print(f"Error in keyword matching: {e}")
            return 0.0
    
    def skills_matching_score(self, resume_text, job_description):
        """Calculate skills matching score"""
        try:
            # Extract skills from both texts
            resume_skills = set(skill.lower() for skill in self.text_processor.extract_skills(resume_text))
            job_skills = set(skill.lower() for skill in self.text_processor.extract_skills(job_description))
            
            if not job_skills:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(resume_skills.intersection(job_skills))
            union = len(resume_skills.union(job_skills))
            
            jaccard_score = intersection / union if union > 0 else 0.0
            
            # Also calculate percentage of job skills found in resume
            job_skills_found = intersection / len(job_skills) if job_skills else 0.0
            
            # Take weighted average
            return (jaccard_score * 0.4 + job_skills_found * 0.6)
            
        except Exception as e:
            print(f"Error in skills matching: {e}")
            return 0.0
    
    def experience_matching_score(self, resume_text, job_description):
        """Calculate experience matching score"""
        try:
            resume_exp = self.text_processor.extract_experience_years(resume_text)
            job_exp = self.extract_required_experience(job_description)
            
            if job_exp == 0:
                return 1.0  # No experience requirement
            
            if resume_exp >= job_exp:
                return 1.0
            elif resume_exp >= job_exp * 0.7:  # 70% of required experience
                return 0.8
            elif resume_exp >= job_exp * 0.5:  # 50% of required experience
                return 0.6
            else:
                return resume_exp / job_exp if job_exp > 0 else 0.0
                
        except Exception as e:
            print(f"Error in experience matching: {e}")
            return 0.0
    
    def extract_important_keywords(self, text, num_keywords=20):
        """Extract important keywords using TF-IDF"""
        try:
            processed_text = self.text_processor.preprocess_for_similarity(text)
            
            if not processed_text:
                return []
            
            # Fit TF-IDF on the text
            tfidf_matrix = self.vectorizer.fit_transform([processed_text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            keywords = [keyword for keyword, score in keyword_scores[:num_keywords] if score > 0]
            return keywords
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def extract_required_experience(self, job_description):
        """Extract required years of experience from job description"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:minimum|min|at least)\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*to\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)'
        ]
        
        text_lower = job_description.lower()
        years = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    # For range patterns, take the minimum
                    years.append(int(match[0]))
                else:
                    years.append(int(match))
        
        return min(years) if years else 0
    
    def analyze_skill_gaps(self, resume_text, job_description):
        """Analyze skill gaps between resume and job requirements"""
        resume_skills = set(skill.lower() for skill in self.text_processor.extract_skills(resume_text))
        job_skills = set(skill.lower() for skill in self.text_processor.extract_skills(job_description))
        
        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        additional_skills = resume_skills - job_skills
        
        return {
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills),
            'additional_skills': list(additional_skills),
            'skill_match_percentage': len(matching_skills) / len(job_skills) * 100 if job_skills else 0
        }
    
    def categorize_job_role(self, job_description):
        """Categorize job role based on description"""
        job_desc_lower = job_description.lower()
        
        for category, keywords in config.JOB_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in job_desc_lower:
                    return category
        
        return 'general'
    
    def get_matching_recommendations(self, resume_text, job_description):
        """Get recommendations to improve resume matching"""
        recommendations = []
        
        # Analyze skill gaps
        skill_analysis = self.analyze_skill_gaps(resume_text, job_description)
        
        if skill_analysis['missing_skills']:
            missing_skills_str = ', '.join(skill_analysis['missing_skills'][:5])  # Show top 5
            recommendations.append(f"🎯 **Add missing skills**: {missing_skills_str}")
        
        # Check experience requirements
        resume_exp = self.text_processor.extract_experience_years(resume_text)
        required_exp = self.extract_required_experience(job_description)
        
        if required_exp > resume_exp:
            recommendations.append(f"💼 **Experience Gap**: Position requires {required_exp} years, highlight relevant projects or internships")
        
        # Check for important keywords
        job_keywords = self.extract_important_keywords(job_description, 10)
        resume_lower = resume_text.lower()
        missing_keywords = [kw for kw in job_keywords if kw.lower() not in resume_lower]
        
        if missing_keywords:
            missing_kw_str = ', '.join(missing_keywords[:3])
            recommendations.append(f"🔍 **Include key terms**: {missing_kw_str}")
        
        # Check resume sections
        resume_sections = self.text_processor.extract_entities(resume_text)
        
        if not resume_sections.get('ORG'):
            recommendations.append("🏢 **Add company names** to highlight work experience")
        
        if skill_analysis['skill_match_percentage'] < 50:
            recommendations.append("📈 **Improve skill relevance**: Focus on skills mentioned in job description")
        
        return recommendations
    
    def batch_resume_ranking(self, resumes_data, job_description):
        """Rank multiple resumes against a job description"""
        rankings = []
        
        for i, (resume_name, resume_text) in enumerate(resumes_data):
            score_data = self.calculate_similarity_score(resume_text, job_description)
            
            rankings.append({
                'rank': i + 1,
                'name': resume_name,
                'overall_score': score_data['overall_score'],
                'method_scores': score_data['method_scores']
            })
        
        # Sort by overall score
        rankings.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Update ranks
        for i, resume in enumerate(rankings):
            resume['rank'] = i + 1
        
        return rankings