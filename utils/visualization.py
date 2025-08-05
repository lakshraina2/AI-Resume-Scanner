import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import config

class VisualizationHelper:
    """Helper class for creating visualizations in the resume scanner"""
    
    def __init__(self):
        self.colors = config.CHART_COLORS
        self.height = config.CHART_HEIGHT
        self.width = config.CHART_WIDTH
    
    def create_score_gauge(self, score, title="Resume Score"):
        """Create a gauge chart for overall score"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 20}},
            delta = {'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': 'lightgray'},
                    {'range': [50, 70], 'color': 'yellow'},
                    {'range': [70, 85], 'color': 'lightgreen'},
                    {'range': [85, 100], 'color': 'green'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    
    def create_category_scores_bar(self, category_scores):
        """Create bar chart for category scores"""
        categories = list(category_scores.keys())
        scores = list(category_scores.values())
        
        # Color bars based on score
        colors = []
        for score in scores:
            if score >= 80:
                colors.append('#2E8B57')  # Green
            elif score >= 60:
                colors.append('#FFD700')  # Gold
            else:
                colors.append('#FF6347')  # Red
        
        fig = go.Figure(data=[
            go.Bar(x=categories, y=scores, marker_color=colors, text=scores, textposition='auto')
        ])
        
        fig.update_layout(
            title="Score Breakdown by Category",
            xaxis_title="Category",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 100]),
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_skills_comparison_chart(self, matching_skills, missing_skills, additional_skills):
        """Create skills comparison chart"""
        skills_data = {
            'Matching Skills': len(matching_skills),
            'Missing Skills': len(missing_skills),
            'Additional Skills': len(additional_skills)
        }
        
        colors = ['#2E8B57', '#FF6347', '#4682B4']
        
        fig = go.Figure(data=[
            go.Bar(x=list(skills_data.keys()), y=list(skills_data.values()), 
                   marker_color=colors, text=list(skills_data.values()), textposition='auto')
        ])
        
        fig.update_layout(
            title="Skills Analysis",
            xaxis_title="Skill Category",
            yaxis_title="Number of Skills",
            height=350,
            showlegend=False
        )
        
        return fig
    
    def create_skills_pie_chart(self, skills_data):
        """Create pie chart for skills distribution"""
        if not any(skills_data.values()):
            return None
        
        labels = list(skills_data.keys())
        values = list(skills_data.values())
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title="Skills Distribution",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_method_scores_radar(self, method_scores):
        """Create radar chart for different matching methods"""
        categories = list(method_scores.keys())
        values = list(method_scores.values())
        
        # Close the radar chart
        categories += [categories[0]]
        values += [values[0]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Matching Scores',
            line_color='blue'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Matching Method Scores",
            height=400
        )
        
        return fig
    
    def create_experience_timeline(self, companies, designations):
        """Create timeline visualization for experience"""
        if not companies and not designations:
            return None
        
        # Create dummy timeline data (in real implementation, would extract dates)
        timeline_data = []
        
        for i, company in enumerate(companies[:5]):  # Show max 5 companies
            designation = designations[i] if i < len(designations) else "Position"
            timeline_data.append({
                'Company': company,
                'Position': designation,
                'Year': f"Year {i+1}",  # Placeholder
                'Duration': 1  # Placeholder
            })
        
        if not timeline_data:
            return None
        
        df = pd.DataFrame(timeline_data)
        
        fig = px.bar(df, x='Duration', y='Company', orientation='h',
                     title='Experience Timeline', 
                     hover_data=['Position'],
                     height=300)
        
        return fig
    
    def create_word_cloud_figure(self, text, title="Word Cloud"):
        """Create word cloud visualization"""
        if not text:
            return None
        
        try:
            # Generate word cloud
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='white',
                colormap='viridis',
                max_words=100
            ).generate(text)
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title, fontsize=16, fontweight='bold')
            
            return fig
        except Exception as e:
            print(f"Error creating word cloud: {e}")
            return None
    
    def create_comparison_table(self, resume_data, job_requirements):
        """Create comparison table between resume and job requirements"""
        comparison_data = {
            'Aspect': ['Skills Match', 'Experience', 'Education', 'Keywords'],
            'Resume': [
                f"{len(resume_data.get('skills', []))} skills",
                f"{resume_data.get('experience_years', 0)} years",
                f"{len(resume_data.get('education', []))} qualifications",
                "Various keywords"
            ],
            'Job Requirements': [
                "Required skills",
                "Experience needed",
                "Education required",
                "Key terms"
            ],
            'Match Status': ['✅', '⚠️', '✅', '⚠️']  # Placeholder
        }
        
        df = pd.DataFrame(comparison_data)
        return df
    
    def create_resume_statistics_chart(self, stats):
        """Create chart showing resume statistics"""
        stat_names = list(stats.keys())
        stat_values = list(stats.values())
        
        fig = go.Figure(data=[
            go.Bar(x=stat_names, y=stat_values, marker_color='lightblue',
                   text=stat_values, textposition='auto')
        ])
        
        fig.update_layout(
            title="Resume Statistics",
            xaxis_title="Metric",
            yaxis_title="Count",
            height=350
        )
        
        return fig

def display_score_with_color(score, label="Score"):
    """Display score with color coding"""
    if score >= 80:
        color = "#2E8B57"  # Green
        emoji = "🟢"
    elif score >= 60:
        color = "#FFD700"  # Gold
        emoji = "🟡"
    else:
        color = "#FF6347"  # Red
        emoji = "🔴"
    
    st.markdown(f"### {emoji} {label}: <span style='color: {color}'>{score:.1f}%</span>", 
                unsafe_allow_html=True)

def display_grade_badge(grade):
    """Display grade as a badge"""
    grade_colors = {
        'A+': '#2E8B57', 'A': '#32CD32', 'A-': '#9ACD32',
        'B+': '#FFD700', 'B': '#FFA500', 'B-': '#FF8C00',
        'C+': '#FF6347', 'C': '#DC143C', 'C-': '#B22222',
        'D': '#8B0000'
    }
    
    color = grade_colors.get(grade, '#808080')
    
    st.markdown(f"""
    <div style='
        background-color: {color}; 
        color: white; 
        padding: 10px 20px; 
        border-radius: 20px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 18px; 
        width: fit-content; 
        margin: 10px auto;
    '>
        Grade: {grade}
    </div>
    """, unsafe_allow_html=True)

def create_progress_bar(value, max_value=100, label="Progress"):
    """Create a styled progress bar"""
    percentage = min(value / max_value * 100, 100)
    
    if percentage >= 80:
        color = "#2E8B57"
    elif percentage >= 60:
        color = "#FFD700"
    else:
        color = "#FF6347"
    
    st.markdown(f"""
    <div style='margin: 10px 0;'>
        <div style='font-weight: bold; margin-bottom: 5px;'>{label}: {value:.1f}%</div>
        <div style='background-color: #f0f0f0; border-radius: 10px; overflow: hidden;'>
            <div style='
                background-color: {color}; 
                width: {percentage}%; 
                height: 20px; 
                border-radius: 10px;
                transition: width 0.3s ease;
            '></div>
        </div>
    </div>
    """, unsafe_allow_html=True)