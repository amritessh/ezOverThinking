# frontend/components/analytics_dashboard.py
"""
Analytics Dashboard Component - Interactive charts and insights
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Interactive analytics dashboard with real-time insights"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        
        # Color schemes
        self.colors = {
            'primary': '#FF6B6B',
            'secondary': '#4ECDC4',
            'accent': '#45B7D1',
            'warning': '#FFA07A',
            'danger': '#FF4757',
            'success': '#2ED573',
            'anxiety_colors': {
                'calm': '#2ED573',
                'mild': '#FFA07A',
                'moderate': '#FF6B6B',
                'high': '#FF4757',
                'extreme': '#8B0000'
            }
        }
    
    def render(self):
        """Render the complete analytics dashboard"""
        # Dashboard header
        self.render_dashboard_header()
        
        # Time range selector
        time_range = self.render_time_range_selector()
        
        # Key metrics overview
        self.render_key_metrics()
        
        # Main analytics sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Anxiety Trends",
            "💬 Conversation Patterns", 
            "🤖 Agent Performance",
            "🔮 Predictions & Insights"
        ])
        
        with tab1:
            self.render_anxiety_analytics(time_range)
        
        with tab2:
            self.render_conversation_analytics(time_range)
        
        with tab3:
            self.render_agent_analytics(time_range)
        
        with tab4:
            self.render_predictions_insights(time_range)
    
    def render_dashboard_header(self):
        """Render dashboard header"""
        st.markdown("""
        <div class="analytics-card">
            <h2>📊 Analytics Dashboard</h2>
            <p>Deep insights into your overthinking patterns, anxiety trends, and conversation analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_time_range_selector(self):
        """Render time range selector"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            time_range = st.selectbox(
                "📅 Time Range",
                ["Last Hour", "Last Day", "Last Week", "Last Month", "All Time"],
                index=2
            )
        
        with col2:
            auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
        
        with col3:
            if st.button("📊 Refresh Data"):
                st.rerun()
        
        return time_range
    
    def render_key_metrics(self):
        """Render key metrics overview"""
        st.markdown("### 🎯 Key Metrics")
        
        # Get mock data for demo (replace with API calls)
        metrics_data = self.get_metrics_data()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            self.render_metric_card(
                "Total Conversations",
                metrics_data['total_conversations'],
                "+12% vs last week",
                "💬"
            )
        
        with col2:
            self.render_metric_card(
                "Avg Anxiety Level",
                metrics_data['avg_anxiety_level'],
                "+0.3 vs yesterday",
                "🌡️"
            )
        
        with col3:
            self.render_metric_card(
                "Peak Anxiety Events",
                metrics_data['peak_events'],
                "3 this week",
                "🆘"
            )
        
        with col4:
            self.render_metric_card(
                "Messages Sent",
                metrics_data['total_messages'],
                "+45% vs last week",
                "📨"
            )
        
        with col5:
            self.render_metric_card(
                "Time Spent",
                f"{metrics_data['time_spent']}h",
                "2.3h today",
                "⏱️"
            )
    
    def render_metric_card(self, title: str, value: str, subtitle: str, emoji: str):
        """Render individual metric card"""
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{emoji}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
            <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.5rem;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_anxiety_analytics(self, time_range: str):
        """Render anxiety trends and analytics"""
        st.markdown("#### 📈 Anxiety Level Trends")
        
        # Generate anxiety trend data
        anxiety_data = self.generate_anxiety_trend_data(time_range)
        
        # Anxiety level over time chart
        fig_anxiety = go.Figure()
        
        fig_anxiety.add_trace(go.Scatter(
            x=anxiety_data['timestamp'],
            y=anxiety_data['anxiety_numeric'],
            mode='lines+markers',
            name='Anxiety Level',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=8, color=anxiety_data['anxiety_color']),
            hovertemplate='<b>%{text}</b><br>Time: %{x}<br>Level: %{customdata}<extra></extra>',
            text=anxiety_data['anxiety_level'],
            customdata=anxiety_data['anxiety_level']
        ))
        
        fig_anxiety.update_layout(
            title="Anxiety Level Progression",
            xaxis_title="Time",
            yaxis_title="Anxiety Level",
            yaxis=dict(
                tickmode='array',
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Calm', 'Mild', 'Moderate', 'High', 'Extreme']
            ),
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig_anxiety, use_container_width=True)
        
        # Anxiety distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Anxiety level distribution pie chart
            anxiety_counts = anxiety_data['anxiety_level'].value_counts()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=anxiety_counts.index,
                values=anxiety_counts.values,
                hole=0.4,
                marker_colors=[self.colors['anxiety_colors'][level] for level in anxiety_counts.index]
            )])
            
            fig_pie.update_layout(
                title="Anxiety Distribution",
                template='plotly_white',
                height=300
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Anxiety triggers analysis
            st.markdown("#### 🎯 Top Anxiety Triggers")
            
            triggers = [
                {"trigger": "Social interactions", "count": 15, "percentage": 35},
                {"trigger": "Work/deadlines", "count": 12, "percentage": 28},
                {"trigger": "Health concerns", "count": 8, "percentage": 19},
                {"trigger": "Technology issues", "count": 5, "percentage": 12},
                {"trigger": "Other", "count": 3, "percentage": 7}
            ]
            
            for trigger in triggers:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                            padding: 0.5rem; margin: 0.25rem 0; background: #F8F9FA; border-radius: 8px;">
                    <span>{trigger['trigger']}</span>
                    <span><strong>{trigger['count']}</strong> ({trigger['percentage']}%)</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Anxiety patterns analysis
        st.markdown("#### 🔍 Anxiety Patterns")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Most Anxious Time**: 2-4 PM")
        
        with col2:
            st.warning("**Longest Streak**: 5 days moderate+")
        
        with col3:
            st.success("**Recovery Time**: Avg 2.3 hours")
    
    def render_conversation_analytics(self, time_range: str):
        """Render conversation patterns and analytics"""
        st.markdown("#### 💬 Conversation Patterns")
        
        # Conversation flow analysis
        flow_data = self.generate_conversation_flow_data()
        
        # Messages per conversation chart
        fig_messages = go.Figure()
        
        fig_messages.add_trace(go.Bar(
            x=flow_data['conversation_id'],
            y=flow_data['message_count'],
            marker_color=self.colors['secondary'],
            name='Messages per Conversation'
        ))
        
        fig_messages.update_layout(
            title="Messages per Conversation",
            xaxis_title="Conversation",
            yaxis_title="Message Count",
            template='plotly_white',
            height=300
        )
        
        st.plotly_chart(fig_messages, use_container_width=True)
        
        # Conversation insights
        col1, col2 = st.columns(2)
        
        with col1:
            # Conversation duration analysis
            st.markdown("#### ⏱️ Conversation Duration")
            
            duration_data = {
                'duration_range': ['< 5 min', '5-15 min', '15-30 min', '30-60 min', '> 1 hour'],
                'count': [8, 15, 12, 7, 3],
                'percentage': [18, 33, 27, 16, 7]
            }
            
            fig_duration = go.Figure(data=[go.Bar(
                x=duration_data['duration_range'],
                y=duration_data['count'],
                marker_color=self.colors['accent'],
                text=duration_data['percentage'],
                texttemplate='%{text}%',
                textposition='outside'
            )])
            
            fig_duration.update_layout(
                title="Conversation Duration Distribution",
                xaxis_title="Duration",
                yaxis_title="Count",
                template='plotly_white',
                height=300
            )
            
            st.plotly_chart(fig_duration, use_container_width=True)
        
        with col2:
            # Topic analysis
            st.markdown("#### 📋 Most Discussed Topics")
            
            topics = [
                {"topic": "Relationships", "mentions": 23, "trend": "↑"},
                {"topic": "Work stress", "mentions": 19, "trend": "↑"},
                {"topic": "Health worries", "mentions": 15, "trend": "↓"},
                {"topic": "Social events", "mentions": 12, "trend": "→"},
                {"topic": "Technology", "mentions": 8, "trend": "↑"},
                {"topic": "Finance", "mentions": 6, "trend": "↓"}
            ]
            
            for i, topic in enumerate(topics):
                trend_color = {
                    "↑": "#2ED573",
                    "↓": "#FF4757", 
                    "→": "#FFA07A"
                }.get(topic['trend'], "#4ECDC4")
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                            padding: 0.75rem; margin: 0.5rem 0; background: #F8F9FA; border-radius: 8px;
                            border-left: 4px solid {trend_color};">
                    <div>
                        <strong>{topic['topic']}</strong><br>
                        <small>{topic['mentions']} mentions</small>
                    </div>
                    <div style="font-size: 1.5rem; color: {trend_color};">
                        {topic['trend']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Word cloud simulation
        st.markdown("#### ☁️ Frequently Used Words")
        
        # Create a simple word frequency chart
        words_data = {
            'word': ['worried', 'scared', 'anxious', 'concerned', 'nervous', 'stressed', 'overthinking', 'panic'],
            'frequency': [45, 32, 38, 28, 25, 30, 42, 18]
        }
        
        fig_words = go.Figure(data=[go.Bar(
            x=words_data['frequency'],
            y=words_data['word'],
            orientation='h',
            marker_color=self.colors['warning']
        )])
        
        fig_words.update_layout(
            title="Most Frequently Used Words",
            xaxis_title="Frequency",
            yaxis_title="Words",
            template='plotly_white',
            height=300
        )
        
        st.plotly_chart(fig_words, use_container_width=True)
    
    def render_agent_analytics(self, time_range: str):
        """Render agent performance analytics"""
        st.markdown("#### 🤖 Agent Performance Analysis")
        
        # Agent interaction data
        agent_data = self.generate_agent_performance_data()
        
        # Agent response times
        col1, col2 = st.columns(2)
        
        with col1:
            fig_response_times = go.Figure()
            
            fig_response_times.add_trace(go.Bar(
                x=agent_data['agent_name'],
                y=agent_data['avg_response_time'],
                marker_color=agent_data['color'],
                name='Avg Response Time (s)'
            ))
            
            fig_response_times.update_layout(
                title="Agent Response Times",
                xaxis_title="Agent",
                yaxis_title="Response Time (seconds)",
                template='plotly_white',
                height=300,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_response_times, use_container_width=True)
        
        with col2:
            # Agent effectiveness scores
            fig_effectiveness = go.Figure()
            
            fig_effectiveness.add_trace(go.Scatter(
                x=agent_data['interactions'],
                y=agent_data['effectiveness_score'],
                mode='markers+text',
                marker=dict(
                    size=agent_data['anxiety_increase'],
                    color=agent_data['color'],
                    sizemode='diameter',
                    sizeref=2,
                    opacity=0.7
                ),
                text=agent_data['agent_short_name'],
                textposition='middle center',
                textfont=dict(color='white', size=10)
            ))
            
            fig_effectiveness.update_layout(
                title="Agent Effectiveness vs Interactions",
                xaxis_title="Total Interactions",
                yaxis_title="Effectiveness Score",
                template='plotly_white',
                height=300
            )
            
            st.plotly_chart(fig_effectiveness, use_container_width=True)
        
        # Agent leaderboard
        st.markdown("#### 🏆 Agent Leaderboard")
        
        # Sort agents by effectiveness
        leaderboard = sorted(
            zip(agent_data['agent_name'], agent_data['effectiveness_score'], 
                agent_data['interactions'], agent_data['anxiety_increase']),
            key=lambda x: x[1], reverse=True
        )
        
        for i, (agent, score, interactions, anxiety_boost) in enumerate(leaderboard):
            position_emoji = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅"][i]
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 1rem; margin: 0.5rem 0; background: #F8F9FA; border-radius: 8px;
                        border-left: 4px solid {self.colors['primary']};">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 1rem;">{position_emoji}</span>
                    <div>
                        <strong>{agent.replace('Agent', '')}</strong><br>
                        <small>{interactions} interactions</small>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.2rem; font-weight: 600;">{score:.1f}/10</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">+{anxiety_boost:.1f} avg anxiety</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_predictions_insights(self, time_range: str):
        """Render predictions and insights"""
        st.markdown("#### 🔮 AI Predictions & Insights")
        
        # Anxiety prediction chart
        prediction_data = self.generate_prediction_data()
        
        fig_prediction = go.Figure()
        
        # Historical data
        fig_prediction.add_trace(go.Scatter(
            x=prediction_data['historical_time'],
            y=prediction_data['historical_anxiety'],
            mode='lines+markers',
            name='Historical',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=6)
        ))
        
        # Predicted data
        fig_prediction.add_trace(go.Scatter(
            x=prediction_data['future_time'],
            y=prediction_data['predicted_anxiety'],
            mode='lines+markers',
            name='Predicted',
            line=dict(color=self.colors['warning'], width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        # Confidence interval
        fig_prediction.add_trace(go.Scatter(
            x=prediction_data['future_time'],
            y=prediction_data['upper_bound'],
            mode='lines',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False,
            name='Upper Bound'
        ))
        
        fig_prediction.add_trace(go.Scatter(
            x=prediction_data['future_time'],
            y=prediction_data['lower_bound'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(255, 160, 122, 0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False,
            name='Confidence Interval'
        ))
        
        fig_prediction.update_layout(
            title="24-Hour Anxiety Level Prediction",
            xaxis_title="Time",
            yaxis_title="Predicted Anxiety Level",
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig_prediction, use_container_width=True)
        
        # Insights and recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💡 Key Insights")
            
            insights = [
                "🔍 You tend to overthink most between 2-4 PM",
                "📱 Social media triggers increase anxiety by 23%",
                "☕ Caffeine correlation: +0.3 anxiety increase",
                "🎯 Work deadlines are your primary trigger",
                "🌙 Evening conversations last 40% longer",
                "📈 Anxiety peaks on Mondays and Thursdays"
            ]
            
            for insight in insights:
                st.markdown(f"- {insight}")
        
        with col2:
            st.markdown("#### 🎯 Personalized Recommendations")
            
            recommendations = [
                "⏰ Schedule important tasks before 2 PM",
                "📵 Limit social media during peak hours",
                "🧘 Try 5-minute breathing exercises",
                "📅 Plan buffer time for deadlines",
                "🌅 Start conversations earlier in the day",
                "💪 Build Monday motivation routines"
            ]
            
            for rec in recommendations:
                st.markdown(f"- {rec}")
        
        # Risk assessment
        st.markdown("#### ⚠️ Risk Assessment")
        
        risk_factors = [
            {"factor": "Upcoming deadline", "risk": "High", "impact": 85},
            {"factor": "Social event tomorrow", "risk": "Medium", "impact": 60},
            {"factor": "Caffeine intake", "risk": "Low", "impact": 25},
            {"factor": "Sleep quality", "risk": "Medium", "impact": 45}
        ]
        
        for factor in risk_factors:
            risk_color = {
                "High": "#FF4757",
                "Medium": "#FFA07A",
                "Low": "#2ED573"
            }.get(factor['risk'])
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 0.75rem; margin: 0.5rem 0; background: #F8F9FA; border-radius: 8px;
                        border-left: 4px solid {risk_color};">
                <div>
                    <strong>{factor['factor']}</strong><br>
                    <span style="color: {risk_color};">{factor['risk']} Risk</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.2rem; font-weight: 600;">{factor['impact']}%</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">Impact</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def get_metrics_data(self):
        """Get metrics data (mock for demo)"""
        return {
            'total_conversations': 47,
            'avg_anxiety_level': '2.8/5',
            'peak_events': 5,
            'total_messages': 234,
            'time_spent': 12.5
        }
    
    def generate_anxiety_trend_data(self, time_range: str):
        """Generate mock anxiety trend data"""
        # Create time series based on range
        if time_range == "Last Hour":
            periods = 12
            freq = '5T'
        elif time_range == "Last Day":
            periods = 24
            freq = 'H'
        elif time_range == "Last Week":
            periods = 7
            freq = 'D'
        else:
            periods = 30
            freq = 'D'
        
        dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
        
        # Generate realistic anxiety progression
        base_anxiety = np.random.normal(2.5, 0.5, periods)
        base_anxiety = np.clip(base_anxiety, 1, 5)
        
        # Convert to categorical
        anxiety_levels = []
        anxiety_colors = []
        for val in base_anxiety:
            if val < 1.5:
                level = 'calm'
            elif val < 2.5:
                level = 'mild'
            elif val < 3.5:
                level = 'moderate'
            elif val < 4.5:
                level = 'high'
            else:
                level = 'extreme'
            
            anxiety_levels.append(level)
            anxiety_colors.append(self.colors['anxiety_colors'][level])
        
        return pd.DataFrame({
            'timestamp': dates,
            'anxiety_numeric': base_anxiety,
            'anxiety_level': anxiety_levels,
            'anxiety_color': anxiety_colors
        })
    
    def generate_conversation_flow_data(self):
        """Generate mock conversation flow data"""
        return pd.DataFrame({
            'conversation_id': [f'Conv {i+1}' for i in range(10)],
            'message_count': np.random.randint(5, 25, 10),
            'duration_minutes': np.random.randint(10, 120, 10),
            'final_anxiety': np.random.randint(1, 5, 10)
        })
    
    def generate_agent_performance_data(self):
        """Generate mock agent performance data"""
        agents = [
            'IntakeSpecialistAgent',
            'CatastropheEscalatorAgent', 
            'TimelinePanicGeneratorAgent',
            'ProbabilityTwisterAgent',
            'SocialAnxietyAmplifierAgent',
            'FalseComfortProviderAgent'
        ]
        
        return {
            'agent_name': agents,
            'agent_short_name': ['Intake', 'Catastrophe', 'Timeline', 'Probability', 'Social', 'Comfort'],
            'avg_response_time': [1.2, 2.1, 1.8, 2.5, 1.9, 1.7],
            'effectiveness_score': [8.5, 9.2, 7.8, 8.9, 8.1, 7.5],
            'interactions': [45, 52, 38, 41, 49, 35],
            'anxiety_increase': [0.8, 1.5, 1.2, 1.1, 1.3, 0.9],
            'color': [self.colors['primary'], self.colors['danger'], self.colors['warning'], 
                     self.colors['accent'], self.colors['secondary'], self.colors['success']]
        }
    
    def generate_prediction_data(self):
        """Generate mock prediction data"""
        # Historical data (last 24 hours)
        hist_time = pd.date_range(end=datetime.now(), periods=24, freq='H')
        hist_anxiety = np.random.normal(2.5, 0.7, 24)
        hist_anxiety = np.clip(hist_anxiety, 1, 5)
        
        # Future prediction (next 24 hours)
        future_time = pd.date_range(start=datetime.now(), periods=24, freq='H')
        predicted_anxiety = np.random.normal(2.8, 0.6, 24)
        predicted_anxiety = np.clip(predicted_anxiety, 1, 5)
        
        # Confidence bounds
        upper_bound = np.clip(predicted_anxiety + 0.5, 1, 5)
        lower_bound = np.clip(predicted_anxiety - 0.5, 1, 5)
        
        return {
            'historical_time': hist_time,
            'historical_anxiety': hist_anxiety,
            'future_time': future_time,
            'predicted_anxiety': predicted_anxiety,
            'upper_bound': upper_bound,
            'lower_bound': lower_bound
        }