import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import config

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model
def load_spacy_model():
    """Load spaCy model for NLP processing"""
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        print("spaCy model 'en_core_web_sm' not found. Please install it using:")
        print("python -m spacy download en_core_web_sm")
        return None

class TextProcessor:
    """Text processing utilities for resume analysis"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.nlp = load_spacy_model()
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text):
        """Remove stopwords from text"""
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def lemmatize_text(self, text):
        """Lemmatize text using NLTK"""
        words = word_tokenize(text)
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)
    
    def extract_entities(self, text):
        """Extract named entities using spaCy"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {
            'PERSON': [],
            'ORG': [],
            'DATE': [],
            'GPE': [],  # Countries, cities, states
            'MONEY': [],
            'PERCENT': []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        return entities
    
    def extract_skills(self, text, skill_list=None):
        """Extract skills from text based on predefined skill list"""
        if skill_list is None:
            skill_list = config.TECHNICAL_SKILLS + config.SOFT_SKILLS
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_list:
            skill_lower = skill.lower()
            # Use word boundaries to match exact skills
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_email(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails
    
    def extract_phone(self, text):
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b',  # 1234567890
            r'\b\d{3}\.\d{3}\.\d{4}\b'  # 123.456.7890
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    def extract_education(self, text):
        """Extract education information from text"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'university',
            'college', 'institute', 'school', 'bsc', 'msc', 'ba', 'ma',
            'btech', 'mtech', 'mba', 'graduation', 'undergraduate', 'postgraduate'
        ]
        
        text_lower = text.lower()
        education_info = []
        
        for keyword in education_keywords:
            if keyword in text_lower:
                # Extract sentences containing education keywords
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        education_info.append(sentence.strip())
        
        return list(set(education_info))
    
    def extract_experience_years(self, text):
        """Extract years of experience from text"""
        experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'experience\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)'
        ]
        
        years = []
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0
    
    def create_word_cloud(self, text, max_words=100):
        """Create word cloud from text"""
        if not text:
            return None
        
        try:
            # Clean text for word cloud
            cleaned_text = self.clean_text(text)
            cleaned_text = self.remove_stopwords(cleaned_text)
            
            if not cleaned_text:
                return None
            
            wordcloud = WordCloud(
                width=800,
                height=400,
                max_words=max_words,
                background_color='white',
                colormap='viridis'
            ).generate(cleaned_text)
            
            return wordcloud
        except Exception as e:
            print(f"Error creating word cloud: {e}")
            return None
    
    def get_text_statistics(self, text):
        """Get basic text statistics"""
        if not text:
            return {}
        
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        stats = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'character_count': len(text),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'unique_words': len(set(word.lower() for word in words if word.isalpha()))
        }
        
        return stats
    
    def preprocess_for_similarity(self, text):
        """Preprocess text for similarity analysis"""
        # Clean text
        cleaned = self.clean_text(text)
        
        # Remove stopwords
        no_stopwords = self.remove_stopwords(cleaned)
        
        # Lemmatize
        lemmatized = self.lemmatize_text(no_stopwords)
        
        return lemmatized