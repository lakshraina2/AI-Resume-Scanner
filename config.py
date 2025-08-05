# Configuration Settings for AI-Powered Resume Scanner

# Application Settings
APP_TITLE = "AI-Powered Resume Scanner"
APP_DESCRIPTION = "Analyze and score resumes against job descriptions using NLP"
VERSION = "1.0.0"

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt']

# Scoring Configuration
MIN_SCORE = 0.0
MAX_SCORE = 100.0
PASSING_SCORE = 70.0

# Similarity Thresholds
SKILL_MATCH_THRESHOLD = 0.7
EXPERIENCE_MATCH_THRESHOLD = 0.6
EDUCATION_MATCH_THRESHOLD = 0.5

# Text Processing Settings
STOPWORDS_LANGUAGES = ['english']
MIN_WORD_LENGTH = 2
MAX_FEATURES_TFIDF = 5000

# Skills Database (Predefined skill categories)
TECHNICAL_SKILLS = [
    'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css', 'react',
    'node.js', 'django', 'flask', 'spring', 'mongodb', 'postgresql',
    'machine learning', 'data science', 'tensorflow', 'pytorch', 'scikit-learn',
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'power bi',
    'aws', 'azure', 'docker', 'kubernetes', 'git', 'jenkins'
]

SOFT_SKILLS = [
    'leadership', 'communication', 'teamwork', 'problem solving',
    'critical thinking', 'time management', 'adaptability', 'creativity',
    'project management', 'analytical thinking', 'collaboration'
]

# Job Categories
JOB_CATEGORIES = {
    'data_science': ['data scientist', 'machine learning engineer', 'data analyst'],
    'software_development': ['software engineer', 'developer', 'programmer'],
    'web_development': ['web developer', 'frontend developer', 'backend developer'],
    'product_management': ['product manager', 'product owner', 'business analyst'],
    'marketing': ['marketing manager', 'digital marketing', 'content marketing']
}

# Visualization Settings
CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
CHART_HEIGHT = 400
CHART_WIDTH = 600

# Database Settings (if using database)
DATABASE_URL = "sqlite:///resume_scanner.db"
TABLE_NAME = "resume_analysis"

# API Settings (if using external APIs)
OPENAI_API_KEY = None  # Set your API key here or use environment variable
MAX_TOKENS = 1000
TEMPERATURE = 0.7