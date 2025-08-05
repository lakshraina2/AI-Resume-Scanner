import re
from pyresparser import ResumeParser
from utils.text_processing import TextProcessor
import config
import tempfile
import os

class ResumeParserModel:
    """Resume parsing model to extract structured information"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def parse_resume_with_pyresparser(self, file_path):
        """Parse resume using pyresparser library"""
        try:
            # Use pyresparser to extract basic information
            data = ResumeParser(file_path).get_extracted_data()
            return {
                'name': data.get('name', ''),
                'email': data.get('email', ''),
                'mobile_number': data.get('mobile_number', ''),
                'skills': data.get('skills', []),
                'education': data.get('college_name', []),
                'degree': data.get('degree', []),
                'designation': data.get('designation', []),
                'companies': data.get('company_names', []),
                'experience': data.get('total_experience', 0),
                'no_of_pages': data.get('no_of_pages', 1)
            }
        except Exception as e:
            print(f"Error with pyresparser: {e}")
            return {}
    
    def parse_resume_manual(self, text):
        """Manual resume parsing using text processing"""
        parsed_data = {
            'name': '',
            'email': [],
            'phone': [],
            'skills': [],
            'education': [],
            'experience_years': 0,
            'entities': {},
            'sections': {}
        }
        
        # Extract contact information
        parsed_data['email'] = self.text_processor.extract_email(text)
        parsed_data['phone'] = self.text_processor.extract_phone(text)
        
        # Extract skills
        parsed_data['skills'] = self.text_processor.extract_skills(text)
        
        # Extract education
        parsed_data['education'] = self.text_processor.extract_education(text)
        
        # Extract experience years
        parsed_data['experience_years'] = self.text_processor.extract_experience_years(text)
        
        # Extract named entities
        parsed_data['entities'] = self.text_processor.extract_entities(text)
        
        # Extract name from entities (first PERSON entity)
        if parsed_data['entities'].get('PERSON'):
            parsed_data['name'] = parsed_data['entities']['PERSON'][0]
        
        # Extract resume sections
        parsed_data['sections'] = self.extract_resume_sections(text)
        
        return parsed_data
    
    def extract_resume_sections(self, text):
        """Extract different sections of resume"""
        sections = {
            'objective': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'projects': '',
            'certifications': '',
            'achievements': ''
        }
        
        # Define section headers patterns
        section_patterns = {
            'objective': r'(?i)(objective|career\s+objective|professional\s+objective)',
            'summary': r'(?i)(summary|professional\s+summary|profile|about)',
            'experience': r'(?i)(experience|work\s+experience|employment|professional\s+experience)',
            'education': r'(?i)(education|academic|qualification|academics)',
            'skills': r'(?i)(skills|technical\s+skills|core\s+competencies|expertise)',
            'projects': r'(?i)(projects|personal\s+projects|academic\s+projects)',
            'certifications': r'(?i)(certifications?|certificates?|training)',
            'achievements': r'(?i)(achievements?|accomplishments?|awards?|honors?)'
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line):
                    current_section = section_name
                    break
            else:
                # Add content to current section
                if current_section and current_section in sections:
                    sections[current_section] += line + ' '
        
        # Clean up sections
        for section in sections:
            sections[section] = sections[section].strip()
        
        return sections
    
    def parse_resume(self, uploaded_file, text_content):
        """Main method to parse resume using multiple approaches"""
        parsed_data = {}
        
        # Try pyresparser first (if file can be saved temporarily)
        if uploaded_file:
            try:
                # Save file temporarily for pyresparser
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_file_path = tmp_file.name
                
                # Parse with pyresparser
                pyresparser_data = self.parse_resume_with_pyresparser(tmp_file_path)
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
                parsed_data.update(pyresparser_data)
                
            except Exception as e:
                print(f"Error with pyresparser approach: {e}")
        
        # Parse manually from text
        manual_data = self.parse_resume_manual(text_content)
        
        # Merge data (manual parsing as fallback/supplement)
        for key, value in manual_data.items():
            if key not in parsed_data or not parsed_data[key]:
                parsed_data[key] = value
        
        # Clean and validate parsed data
        parsed_data = self.clean_parsed_data(parsed_data)
        
        return parsed_data
    
    def clean_parsed_data(self, data):
        """Clean and validate parsed data"""
        cleaned_data = {}
        
        # Handle name
        cleaned_data['name'] = data.get('name', '').strip() if data.get('name') else ''
        
        # Handle contact info
        cleaned_data['email'] = data.get('email', [])
        if isinstance(cleaned_data['email'], str):
            cleaned_data['email'] = [cleaned_data['email']] if cleaned_data['email'] else []
        
        cleaned_data['phone'] = data.get('phone', [])
        if isinstance(cleaned_data['phone'], str):
            cleaned_data['phone'] = [cleaned_data['phone']] if cleaned_data['phone'] else []
        
        # Handle mobile_number from pyresparser
        mobile = data.get('mobile_number', '')
        if mobile and mobile not in cleaned_data['phone']:
            cleaned_data['phone'].append(mobile)
        
        # Handle skills
        skills = data.get('skills', [])
        if isinstance(skills, str):
            skills = [skills]
        cleaned_data['skills'] = [skill.strip() for skill in skills if skill.strip()]
        
        # Handle education
        education = data.get('education', [])
        if isinstance(education, str):
            education = [education]
        cleaned_data['education'] = [edu.strip() for edu in education if edu.strip()]
        
        # Handle experience
        cleaned_data['experience_years'] = data.get('experience_years', 0)
        if data.get('experience') and not cleaned_data['experience_years']:
            # Try to extract years from experience field
            exp_text = str(data.get('experience', ''))
            years = self.text_processor.extract_experience_years(exp_text)
            cleaned_data['experience_years'] = years
        
        # Handle companies and designations
        cleaned_data['companies'] = data.get('companies', [])
        if isinstance(cleaned_data['companies'], str):
            cleaned_data['companies'] = [cleaned_data['companies']] if cleaned_data['companies'] else []
        
        cleaned_data['designations'] = data.get('designation', [])
        if isinstance(cleaned_data['designations'], str):
            cleaned_data['designations'] = [cleaned_data['designations']] if cleaned_data['designations'] else []
        
        # Handle sections
        cleaned_data['sections'] = data.get('sections', {})
        
        # Handle entities
        cleaned_data['entities'] = data.get('entities', {})
        
        # Handle additional fields
        cleaned_data['degree'] = data.get('degree', [])
        if isinstance(cleaned_data['degree'], str):
            cleaned_data['degree'] = [cleaned_data['degree']] if cleaned_data['degree'] else []
        
        cleaned_data['no_of_pages'] = data.get('no_of_pages', 1)
        
        return cleaned_data
    
    def get_resume_summary(self, parsed_data):
        """Generate a summary of parsed resume data"""
        summary = {
            'contact_info_complete': bool(parsed_data.get('name') and parsed_data.get('email')),
            'skills_count': len(parsed_data.get('skills', [])),
            'education_count': len(parsed_data.get('education', [])),
            'experience_years': parsed_data.get('experience_years', 0),
            'companies_count': len(parsed_data.get('companies', [])),
            'has_phone': bool(parsed_data.get('phone')),
            'sections_found': list(parsed_data.get('sections', {}).keys())
        }
        
        return summary