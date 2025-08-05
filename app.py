import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from utils.file_handler import FileHandler, create_file_uploader
from utils.text_processing import TextProcessor
from utils.visualization import VisualizationHelper, display_score_with_color, display_grade_badge, create_progress_bar
from models.resume_parser import ResumeParserModel
from models.job_matcher import JobMatcher
from models.scoring_engine import ScoringEngine
import config

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .recommendation-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #000000; /* Black text for better visibility */
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #000000; /* Black text for better visibility */
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Initialize components
    file_handler = FileHandler()
    text_processor = TextProcessor()
    resume_parser = ResumeParserModel()
    job_matcher = JobMatcher()
    scoring_engine = ScoringEngine()
    viz_helper = VisualizationHelper()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Powered Resume Scanner</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze and score resumes using Natural Language Processing</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Navigation")
        app_mode = st.selectbox(
            "Choose Analysis Mode",
            ["Single Resume Analysis", "Resume vs Job Description", "Batch Resume Ranking", "About"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Features")
        st.markdown("""
        - Resume parsing & extraction
        - Skills analysis
        - Job matching & scoring  
        - Detailed feedback
        - Visual analytics
        """)
    
    if app_mode == "Single Resume Analysis":
        single_resume_analysis(file_handler, text_processor, resume_parser, scoring_engine, viz_helper)
    
    elif app_mode == "Resume vs Job Description":
        resume_vs_job_analysis(file_handler, text_processor, resume_parser, job_matcher, viz_helper)
    
    elif app_mode == "Batch Resume Ranking":
        batch_resume_ranking(file_handler, text_processor, job_matcher, viz_helper)
    
    elif app_mode == "About":
        show_about_page()

def single_resume_analysis(file_handler, text_processor, resume_parser, scoring_engine, viz_helper):
    """Single resume analysis mode"""
    
    st.header("📄 Single Resume Analysis")
    st.write("Upload a resume to get comprehensive analysis and scoring.")
    
    # File upload
    uploaded_file = create_file_uploader("Upload Resume for Analysis", key="single_resume")
    
    if uploaded_file is not None:
        with st.spinner("🔍 Analyzing resume..."):
            # Extract text
            resume_text = file_handler.extract_text(uploaded_file)
            
            if not resume_text:
                st.error("❌ Could not extract text from the uploaded file.")
                return
            
            # Parse resume
            parsed_resume = resume_parser.parse_resume(uploaded_file, resume_text)
            
            # Calculate scores
            score_result = scoring_engine.calculate_overall_score(parsed_resume, resume_text)
            
            # Get text statistics
            text_stats = text_processor.get_text_statistics(resume_text)
            
            # Get improvement suggestions
            suggestions = scoring_engine.get_improvement_suggestions(parsed_resume, resume_text)
        
        # Display results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Overall Score")
            
            # Score gauge
            gauge_fig = viz_helper.create_score_gauge(score_result['overall_score'])
            st.plotly_chart(gauge_fig, use_container_width=True)
            
            # Grade badge
            display_grade_badge(score_result['grade'])
        
        with col2:
            st.subheader("📈 Score Breakdown")
            
            # Category scores
            for category, score in score_result['category_scores'].items():
                create_progress_bar(score, label=category.replace('_', ' ').title())
        
        # Category scores bar chart
        st.subheader("📋 Detailed Score Analysis")
        bar_fig = viz_helper.create_category_scores_bar(score_result['category_scores'])
        st.plotly_chart(bar_fig, use_container_width=True)
        
        # Parsed information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Extracted Information")
            
            info_data = {
                "Name": parsed_resume.get('name', 'Not found'),
                "Email": ', '.join(parsed_resume.get('email', [])) if parsed_resume.get('email') else 'Not found',
                "Phone": ', '.join(parsed_resume.get('phone', [])) if parsed_resume.get('phone') else 'Not found',
                "Experience": f"{parsed_resume.get('experience_years', 0)} years",
                "Skills Count": len(parsed_resume.get('skills', [])),
                "Education Count": len(parsed_resume.get('education', []))
            }
            
            for key, value in info_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("📊 Resume Statistics")
            
            stats_data = {
                "Word Count": text_stats.get('word_count', 0),
                "Sentences": text_stats.get('sentence_count', 0),
                "Unique Words": text_stats.get('unique_words', 0),
                "Avg Words/Sentence": round(text_stats.get('avg_words_per_sentence', 0), 1)
            }
            
            for key, value in stats_data.items():
                st.write(f"**{key}:** {value}")
        
        # Skills analysis
        if parsed_resume.get('skills'):
            st.subheader("🎯 Skills Analysis")
            
            skills_col1, skills_col2 = st.columns(2)
            
            with skills_col1:
                st.write("**Identified Skills:**")
                skills_text = ", ".join(parsed_resume['skills'][:10])  # Show first 10 skills
                if len(parsed_resume['skills']) > 10:
                    skills_text += f" ... and {len(parsed_resume['skills']) - 10} more"
                st.write(skills_text)
            
            with skills_col2:
                # Skills word cloud
                skills_text = " ".join(parsed_resume['skills'])
                wc_fig = viz_helper.create_word_cloud_figure(skills_text, "Skills Word Cloud")
                if wc_fig:
                    st.pyplot(wc_fig)
        
        # Feedback and suggestions
        st.subheader("💡 Feedback & Recommendations")
        
        feedback_col1, feedback_col2 = st.columns(2)
        
        with feedback_col1:
            st.write("**🔍 Analysis Feedback:**")
            for feedback in score_result['feedback']:
                st.markdown(f'<div class="recommendation-box">{feedback}</div>', unsafe_allow_html=True)
        
        with feedback_col2:
            st.write("**✨ Improvement Suggestions:**")
            for suggestion in suggestions:
                st.markdown(f'<div class="success-box">{suggestion}</div>', unsafe_allow_html=True)

def resume_vs_job_analysis(file_handler, text_processor, resume_parser, job_matcher, viz_helper):
    """Resume vs job description analysis mode"""
    
    st.header("🎯 Resume vs Job Description Analysis")
    st.write("Compare how well a resume matches a specific job description.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_resume = create_file_uploader("Upload Resume", key="resume_job_match")
    
    with col2:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste Job Description",
            height=300,
            placeholder="Paste the job description here...",
            key="job_desc_input"
        )
    
    if uploaded_resume is not None and job_description.strip():
        
        with st.spinner("🔍 Analyzing match..."):
            # Extract resume text
            resume_text = file_handler.extract_text(uploaded_resume)
            
            if not resume_text:
                st.error("❌ Could not extract text from the resume.")
                return
            
            # Calculate similarity
            similarity_result = job_matcher.calculate_similarity_score(resume_text, job_description)
            
            # Analyze skill gaps
            skill_gaps = job_matcher.analyze_skill_gaps(resume_text, job_description)
            
            # Get recommendations
            recommendations = job_matcher.get_matching_recommendations(resume_text, job_description)
        
        # Display results
        st.subheader("🎯 Job Match Results")
        
        # Overall match score
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Match score gauge
            gauge_fig = viz_helper.create_score_gauge(
                similarity_result['overall_score'], 
                "Job Match Score"
            )
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Method Scores")
            for method, score in similarity_result['method_scores'].items():
                method_name = method.replace('_', ' ').title()
                create_progress_bar(score, label=method_name)
        
        # Method scores radar chart
        st.subheader("📈 Matching Methods Comparison")
        radar_fig = viz_helper.create_method_scores_radar(similarity_result['method_scores'])
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Skills analysis
        st.subheader("🎯 Skills Gap Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Skills comparison chart
            skills_fig = viz_helper.create_skills_comparison_chart(
                skill_gaps['matching_skills'],
                skill_gaps['missing_skills'],
                skill_gaps['additional_skills']
            )
            st.plotly_chart(skills_fig, use_container_width=True)
        
        with col2:
            st.write(f"**Skill Match Percentage:** {skill_gaps['skill_match_percentage']:.1f}%")
            
            if skill_gaps['matching_skills']:
                st.write("**✅ Matching Skills:**")
                st.write(", ".join(skill_gaps['matching_skills'][:5]))
            
            if skill_gaps['missing_skills']:
                st.write("**❌ Missing Skills:**")
                st.write(", ".join(skill_gaps['missing_skills'][:5]))
        
        # Recommendations
        st.subheader("💡 Improvement Recommendations")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f'<div class="recommendation-box">{i}. {rec}</div>', unsafe_allow_html=True)
        else:
            st.success("🎉 Great match! Your resume aligns well with the job description.")

def batch_resume_ranking(file_handler, text_processor, job_matcher, viz_helper):
    """Batch resume ranking mode"""
    
    st.header("📊 Batch Resume Ranking")
    st.write("Upload multiple resumes and rank them against a job description.")
    
    # Job description input
    job_description = st.text_area(
        "📋 Job Description",
        height=200,
        placeholder="Paste the job description here...",
        key="batch_job_desc"
    )
    
    # Multiple file upload
    uploaded_files = st.file_uploader(
        "📁 Upload Multiple Resumes",
        type=['pdf', 'docx', 'doc', 'txt'],
        accept_multiple_files=True,
        key="batch_resumes"
    )
    
    if job_description.strip() and uploaded_files:
        
        if len(uploaded_files) > 10:
            st.warning("⚠️ Maximum 10 files allowed for batch processing.")
            uploaded_files = uploaded_files[:10]
        
        with st.spinner(f"🔍 Processing {len(uploaded_files)} resumes..."):
            resumes_data = []
            
            # Process each resume
            for uploaded_file in uploaded_files:
                resume_text = file_handler.extract_text(uploaded_file)
                if resume_text:
                    resumes_data.append((uploaded_file.name, resume_text))
            
            if not resumes_data:
                st.error("❌ Could not extract text from any of the uploaded files.")
                return
            
            # Rank resumes
            rankings = job_matcher.batch_resume_ranking(resumes_data, job_description)
        
        # Display results
        st.subheader("🏆 Ranking Results")
        
        # Create ranking dataframe
        ranking_df = pd.DataFrame([
            {
                'Rank': rank['rank'],
                'Resume': rank['name'],
                'Overall Score': f"{rank['overall_score']:.1f}%",
                'TF-IDF Score': f"{rank['method_scores']['tfidf_cosine']:.1f}%",
                'Skills Match': f"{rank['method_scores']['skills_match']:.1f}%",
                'Keyword Match': f"{rank['method_scores']['keyword_match']:.1f}%"
            }
            for rank in rankings
        ])
        
        st.dataframe(ranking_df, use_container_width=True)
        
        # Top 3 visualization
        if len(rankings) >= 3:
            st.subheader("🥇 Top 3 Candidates")
            
            top_3 = rankings[:3]
            names = [r['name'][:20] + '...' if len(r['name']) > 20 else r['name'] for r in top_3]
            scores = [r['overall_score'] for r in top_3]
            
            fig = viz_helper.create_category_scores_bar(dict(zip(names, scores)))
            fig.update_layout(title="Top 3 Resume Scores", xaxis_title="Resume", yaxis_title="Score (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Download results
        csv = ranking_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"resume_ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_about_page():
    """Show about page"""
    
    st.header("ℹ️ About AI-Powered Resume Scanner")
    
    st.markdown("""
    ## 🎯 Overview
    
    The AI-Powered Resume Scanner is a comprehensive tool that uses Natural Language Processing (NLP) 
    and machine learning techniques to analyze resumes and provide intelligent insights.
    
    ## ✨ Key Features
    
    ### 📄 Resume Analysis
    - **Text Extraction**: Supports PDF, DOCX, DOC, and TXT formats
    - **Information Parsing**: Extracts names, contact info, skills, education, and experience
    - **Content Quality Assessment**: Analyzes writing quality and structure
    
    ### 🎯 Job Matching
    - **Similarity Scoring**: Uses TF-IDF and cosine similarity algorithms
    - **Skills Gap Analysis**: Identifies missing and matching skills
    - **Keyword Matching**: Compares important terms and phrases
    
    ### 📊 Scoring System
    - **Comprehensive Scoring**: Multi-dimensional evaluation
    - **Grade Assignment**: Letter grades from A+ to D
    - **Detailed Feedback**: Actionable improvement suggestions
    
    ### 📈 Visualizations
    - **Interactive Charts**: Plotly-based visualizations
    - **Progress Indicators**: Color-coded score displays
    - **Word Clouds**: Visual representation of skills and keywords
    
    ## 🛠️ Technology Stack
    
    - **Framework**: Streamlit
    - **NLP Libraries**: NLTK, spaCy, scikit-learn
    - **Parsing**: PyPDF2, pdfplumber, python-docx
    - **Visualizations**: Plotly, Matplotlib
    - **ML Algorithms**: TF-IDF, Cosine Similarity, Named Entity Recognition
    
    ## 📋 Use Cases
    
    1. **Job Seekers**: Optimize resumes for specific job applications
    2. **HR Professionals**: Screen and rank candidates efficiently
    3. **Recruiters**: Match candidates to job requirements
    4. **Career Counselors**: Provide data-driven resume feedback
    
    ## 🔒 Privacy & Security
    
    - No data is stored permanently
    - Files are processed in memory only
    - Temporary files are cleaned up automatically
    - No personal information is retained
    
    ## Developed By
    
    Lakshay Raina
    
    - https://www.linkedin.com/in/lakshay4444/
    - https://github.com/lakshraina2    
    
    ---
    
    **Version**: {config.VERSION}
    
    
    """.format(config=config))

if __name__ == "__main__":
    main()
