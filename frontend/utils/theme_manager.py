# frontend/utils/theme_manager.py
import streamlit as st
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages UI themes and styling for the Streamlit frontend"""

    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "name": "Dark Mode",
                "primary_color": "#FF6B6B",
                "secondary_color": "#4ECDC4",
                "accent_color": "#45B7D1",
                "background_color": "#1E1E1E",
                "surface_color": "#2D2D2D",
                "text_color": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "border_color": "#404040",
                "success_color": "#2ED573",
                "warning_color": "#FFA07A",
                "error_color": "#FF4757",
                "info_color": "#4ECDC4",
            },
            "light": {
                "name": "Light Mode",
                "primary_color": "#FF6B6B",
                "secondary_color": "#4ECDC4",
                "accent_color": "#45B7D1",
                "background_color": "#F8F9FA",
                "surface_color": "#FFFFFF",
                "text_color": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "border_color": "#E9ECEF",
                "success_color": "#27AE60",
                "warning_color": "#F39C12",
                "error_color": "#E74C3C",
                "info_color": "#3498DB",
            },
            "anxiety": {
                "name": "Anxiety Mode",
                "primary_color": "#FF4757",
                "secondary_color": "#FF6B6B",
                "accent_color": "#FFA07A",
                "background_color": "#2C1810",
                "surface_color": "#3D2317",
                "text_color": "#FFE4E1",
                "text_secondary": "#FFB6C1",
                "border_color": "#8B4513",
                "success_color": "#32CD32",
                "warning_color": "#FFD700",
                "error_color": "#DC143C",
                "info_color": "#87CEEB",
            },
            "calm": {
                "name": "Calm Mode",
                "primary_color": "#4ECDC4",
                "secondary_color": "#45B7D1",
                "accent_color": "#96CEB4",
                "background_color": "#F0F8FF",
                "surface_color": "#FFFFFF",
                "text_color": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "border_color": "#E8F4FD",
                "success_color": "#27AE60",
                "warning_color": "#F39C12",
                "error_color": "#E74C3C",
                "info_color": "#3498DB",
            },
        }

    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme

    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get colors for a specific theme"""
        if theme_name is None:
            theme_name = self.current_theme

        return self.themes.get(theme_name, self.themes["dark"])

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme()
            logger.info(f"✅ Theme changed to: {theme_name}")
            return True
        else:
            logger.error(f"❌ Unknown theme: {theme_name}")
            return False

    def apply_theme(self):
        """Apply the current theme to Streamlit"""
        colors = self.get_theme_colors()

        # Apply custom CSS
        css = f"""
        <style>
        /* Theme Variables */
        :root {{
            --primary-color: {colors['primary_color']};
            --secondary-color: {colors['secondary_color']};
            --accent-color: {colors['accent_color']};
            --background-color: {colors['background_color']};
            --surface-color: {colors['surface_color']};
            --text-color: {colors['text_color']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border_color']};
            --success-color: {colors['success_color']};
            --warning-color: {colors['warning_color']};
            --error-color: {colors['error_color']};
            --info-color: {colors['info_color']};
        }}
        
        /* Global Styles */
        .stApp {{
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
        }}
        
        /* Main Container */
        .main .block-container {{
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color) !important;
        }}
        
        /* Text */
        p, div, span {{
            color: var(--text-color) !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary-color) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        }}
        
        /* Text Input */
        .stTextInput > div > div > input {{
            background-color: var(--surface-color) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2) !important;
        }}
        
        /* Selectbox */
        .stSelectbox > div > div > select {{
            background-color: var(--surface-color) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        /* Sidebar */
        .css-1d391kg {{
            background-color: var(--surface-color) !important;
        }}
        
        /* Cards and Containers */
        .stAlert {{
            background-color: var(--surface-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        /* Success Alert */
        .stAlert[data-baseweb="notification"] {{
            background-color: var(--success-color) !important;
            color: white !important;
        }}
        
        /* Warning Alert */
        .stAlert[data-baseweb="notification"].warning {{
            background-color: var(--warning-color) !important;
            color: white !important;
        }}
        
        /* Error Alert */
        .stAlert[data-baseweb="notification"].error {{
            background-color: var(--error-color) !important;
            color: white !important;
        }}
        
        /* Info Alert */
        .stAlert[data-baseweb="notification"].info {{
            background-color: var(--info-color) !important;
            color: white !important;
        }}
        
        /* Custom Components */
        .theme-card {{
            background-color: var(--surface-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }}
        
        .theme-header {{
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color)) !important;
            color: white !important;
            padding: 1rem 2rem !important;
            border-radius: 10px !important;
            margin-bottom: 2rem !important;
            text-align: center !important;
        }}
        
        .theme-metric {{
            background: linear-gradient(135deg, var(--secondary-color), var(--info-color)) !important;
            color: white !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            text-align: center !important;
            margin: 0.5rem 0 !important;
        }}
        
        /* Anxiety Level Indicators */
        .anxiety-calm {{
            background: linear-gradient(135deg, var(--success-color), #7bed9f) !important;
            color: white !important;
        }}
        
        .anxiety-mild {{
            background: linear-gradient(135deg, var(--warning-color), #ffb347) !important;
            color: white !important;
        }}
        
        .anxiety-moderate {{
            background: linear-gradient(135deg, var(--primary-color), #ff5252) !important;
            color: white !important;
        }}
        
        .anxiety-high {{
            background: linear-gradient(135deg, var(--error-color), #c44569) !important;
            color: white !important;
        }}
        
        .anxiety-extreme {{
            background: linear-gradient(135deg, #8B0000, #B22222) !important;
            color: white !important;
            animation: pulse 2s infinite !important;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .theme-header {{
                padding: 0.5rem 1rem !important;
                font-size: 1.2rem !important;
            }}
            
            .theme-card {{
                padding: 1rem !important;
                margin: 0.5rem 0 !important;
            }}
        }}
        </style>
        """

        st.markdown(css, unsafe_allow_html=True)

    def get_available_themes(self) -> Dict[str, str]:
        """Get list of available themes"""
        return {name: theme["name"] for name, theme in self.themes.items()}

    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Create a custom theme"""
        try:
            required_colors = [
                "primary_color",
                "secondary_color",
                "accent_color",
                "background_color",
                "surface_color",
                "text_color",
                "text_secondary",
                "border_color",
                "success_color",
                "warning_color",
                "error_color",
                "info_color",
            ]

            # Check if all required colors are provided
            for color in required_colors:
                if color not in colors:
                    logger.error(f"❌ Missing required color: {color}")
                    return False

            self.themes[name] = {"name": name.title(), **colors}

            logger.info(f"✅ Custom theme created: {name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating custom theme: {e}")
            return False

    def delete_theme(self, name: str) -> bool:
        """Delete a custom theme"""
        if name in ["dark", "light"]:
            logger.error("❌ Cannot delete default themes")
            return False

        if name in self.themes:
            del self.themes[name]
            if self.current_theme == name:
                self.current_theme = "dark"
            logger.info(f"✅ Theme deleted: {name}")
            return True
        else:
            logger.error(f"❌ Theme not found: {name}")
            return False

    def export_theme(self, name: str) -> Optional[Dict[str, Any]]:
        """Export theme configuration"""
        if name in self.themes:
            return {
                "name": name,
                "colors": self.themes[name],
                "export_timestamp": "2025-07-04T03:55:00Z",
            }
        else:
            logger.error(f"❌ Theme not found: {name}")
            return None

    def import_theme(self, theme_data: Dict[str, Any]) -> bool:
        """Import theme configuration"""
        try:
            name = theme_data.get("name")
            colors = theme_data.get("colors", {})

            if not name or not colors:
                logger.error("❌ Invalid theme data")
                return False

            return self.create_custom_theme(name, colors)

        except Exception as e:
            logger.error(f"❌ Error importing theme: {e}")
            return False

    def get_theme_preview(self, theme_name: str) -> str:
        """Get HTML preview of a theme"""
        colors = self.get_theme_colors(theme_name)

        preview_html = f"""
        <div style="
            background-color: {colors['background_color']};
            color: {colors['text_color']};
            padding: 1rem;
            border-radius: 8px;
            border: 2px solid {colors['border_color']};
            margin: 0.5rem 0;
        ">
            <h3 style="color: {colors['primary_color']};">{colors['name']}</h3>
            <p style="color: {colors['text_secondary']};">Theme Preview</p>
            <div style="
                background-color: {colors['surface_color']};
                padding: 0.5rem;
                border-radius: 4px;
                margin: 0.5rem 0;
            ">
                <span style="color: {colors['success_color']};">Success</span> |
                <span style="color: {colors['warning_color']};">Warning</span> |
                <span style="color: {colors['error_color']};">Error</span> |
                <span style="color: {colors['info_color']};">Info</span>
            </div>
        </div>
        """

        return preview_html
