import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List


class AnalyticsEngine:
    def __init__(self):
        self.color_palette = [
            "#1E88E5", "#43A047", "#FB8C00", "#E53935",
            "#8E24AA", "#00ACC1", "#FDD835", "#6D4C41"
        ]

    def department_placement_chart(self) -> go.Figure:
        departments = ["Computer Science", "Information Tech", "Electronics",
                       "Mechanical", "Civil", "Electrical"]
        total = [120, 80, 90, 70, 60, 50]
        placed = [95, 58, 50, 28, 15, 20]
        not_placed = [t - p for t, p in zip(total, placed)]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Placed", x=departments, y=placed,
            marker_color="#43A047"
        ))
        fig.add_trace(go.Bar(
            name="Not Placed", x=departments, y=not_placed,
            marker_color="#E53935"
        ))
        fig.update_layout(
            barmode="stack",
            title="Department-wise Placement Status",
            xaxis_title="Department", yaxis_title="Students",
            template="plotly_white", height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        return fig

    def salary_distribution_chart(self) -> go.Figure:
        np.random.seed(42)
        salaries = np.concatenate([
            np.random.normal(4.0, 1.0, 200),
            np.random.normal(7.0, 1.5, 150),
            np.random.normal(12.0, 2.0, 80),
            np.random.normal(25.0, 5.0, 30),
        ])
        salaries = np.clip(salaries, 2.5, 50)

        fig = px.histogram(
            x=salaries, nbins=30,
            title="Salary Distribution (LPA)",
            labels={"x": "Salary (LPA)", "y": "Count"},
            color_discrete_sequence=["#1E88E5"],
            template="plotly_white"
        )
        fig.update_layout(height=350)
        return fig

    def monthly_placements_trend(self) -> go.Figure:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        placements = [12, 18, 25, 35, 45, 52, 48, 55, 62, 58, 65, 70]
        applications = [80, 95, 110, 130, 150, 140, 120, 160, 180, 170, 190, 200]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=months, y=placements, name="Placements",
            line=dict(color="#43A047", width=3),
            mode="lines+markers"
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=months, y=applications, name="Applications",
            line=dict(color="#1E88E5", width=2, dash="dash"),
            mode="lines+markers"
        ), secondary_y=True)
        fig.update_layout(
            title="Monthly Placement Trend",
            template="plotly_white", height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig.update_yaxes(title_text="Placements", secondary_y=False)
        fig.update_yaxes(title_text="Applications", secondary_y=True)
        return fig

    def top_skills_demand_chart(self) -> go.Figure:
        skills = ["Python", "Java", "React", "SQL", "AWS", "Docker",
                  "Machine Learning", "Git", "Node.js", "Spring Boot",
                  "TypeScript", "Kubernetes", "Go", "Redis", "GraphQL"]
        demand = [95, 88, 82, 80, 75, 70, 68, 65, 60, 55, 52, 48, 45, 42, 40]

        fig = px.bar(
            x=demand, y=skills, orientation="h",
            title="Top 15 Skills in Demand",
            labels={"x": "Demand Score", "y": "Skill"},
            color=demand,
            color_continuous_scale="Viridis",
            template="plotly_white"
        )
        fig.update_layout(height=500, yaxis=dict(autorange="reversed"))
        return fig

    def skill_demand_heatmap(self) -> go.Figure:
        depts = ["CS", "IT", "ECE", "ME", "CE", "EE"]
        skills = ["Python", "Java", "React", "SQL", "AWS", "Docker",
                  "ML", "C++", "Git", "Docker"]
        np.random.seed(42)
        data = np.array([
            [95, 90, 85, 80, 75, 70, 65, 60, 90, 70],
            [90, 85, 80, 75, 70, 65, 60, 55, 85, 65],
            [70, 65, 50, 70, 55, 40, 45, 80, 70, 40],
            [40, 50, 30, 40, 20, 25, 15, 70, 50, 25],
            [30, 35, 20, 50, 15, 20, 10, 30, 40, 20],
            [35, 40, 25, 45, 20, 20, 10, 25, 45, 20],
        ])

        fig = px.imshow(
            data, labels=dict(x="Skills", y="Department", color="Demand"),
            x=skills, y=depts,
            color_continuous_scale="YlOrRd",
            title="Skill Demand Heatmap by Department",
            aspect="auto"
        )
        fig.update_layout(height=400)
        return fig

    def company_comparison_chart(self) -> go.Figure:
        companies = pd.DataFrame({
            "Company": ["TCS", "Infosys", "Wipro", "Amazon", "Google",
                       "Microsoft", "Accenture", "IBM", "Freshworks", "Zoho"],
            "Min Salary (LPA)": [3.36, 3.60, 3.50, 12.0, 18.0,
                                15.0, 4.50, 4.00, 5.00, 4.50],
            "Max Salary (LPA)": [7.0, 6.50, 6.00, 30.0, 45.0,
                                40.0, 8.00, 12.0, 10.0, 9.00],
            "Min CGPA": [6.0, 6.0, 6.0, 7.0, 7.5,
                        7.0, 6.5, 6.5, 6.5, 6.0],
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Min Salary", x=companies["Company"],
            y=companies["Min Salary (LPA)"],
            marker_color="#90CAF9"
        ))
        fig.add_trace(go.Bar(
            name="Max Salary", x=companies["Company"],
            y=companies["Max Salary (LPA)"],
            marker_color="#1E88E5"
        ))
        fig.add_trace(go.Scatter(
            name="Min CGPA (x5)", x=companies["Company"],
            y=companies["Min CGPA"] * 5,
            mode="lines+markers",
            line=dict(color="#E53935", width=2, dash="dot"),
            yaxis="y2"
        ))
        fig.update_layout(
            title="Company Salary Comparison",
            barmode="group",
            yaxis=dict(title="Salary (LPA)"),
            yaxis2=dict(title="CGPA x5", overlaying="y", side="right",
                       showgrid=False, range=[0, 50]),
            template="plotly_white", height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        return fig

    def placement_probability_gauge(self, probability: float) -> go.Figure:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=probability,
            title={"text": "Placement Probability (%)", "font": {"size": 18}},
            number={"suffix": "%", "font": {"size": 24}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": "#1E88E5", "thickness": 0.3},
                "bgcolor": "white",
                "borderwidth": 2,
                "steps": [
                    {"range": [0, 30], "color": "#FFCDD2"},
                    {"range": [30, 50], "color": "#FFF9C4"},
                    {"range": [50, 70], "color": "#DCEDC8"},
                    {"range": [70, 100], "color": "#C8E6C9"},
                ],
                "threshold": {
                    "line": {"color": "#E53935", "width": 4},
                    "thickness": 0.75,
                    "value": probability,
                },
            }
        ))
        fig.update_layout(height=280, margin=dict(t=60, b=20, l=30, r=30))
        return fig

    def ats_radar_chart(self, section_scores: Dict) -> go.Figure:
        categories = []
        values = []
        for section, data in section_scores.items():
            if isinstance(data, dict):
                categories.append(section.replace("_", " ").title())
                values.append(data.get("score", 0))

        if not categories:
            return go.Figure()

        fig = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(30, 136, 229, 0.2)",
            line=dict(color="#1E88E5", width=2),
            name="ATS Score"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Resume ATS Profile",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        return fig

    def comparison_bar(self, metrics: Dict[str, float], title: str) -> go.Figure:
        names = list(metrics.keys())
        values = list(metrics.values())

        fig = px.bar(
            x=names, y=values,
            title=title,
            labels={"x": "Metric", "y": "Score (%)"},
            color=values,
            color_continuous_scale="RdYlGn",
            range_y=[0, 100],
            template="plotly_white"
        )
        fig.update_layout(height=350)
        return fig

    def company_scatter(self) -> go.Figure:
        companies = pd.DataFrame({
            "Company": ["TCS", "Infosys", "Wipro", "Amazon", "Google",
                       "Microsoft", "Accenture", "IBM", "Freshworks", "Zoho",
                       "SAP Labs", "Atlassian", "Flipkart", "Razorpay", "Nvidia"],
            "Avg Salary": [4.2, 4.0, 3.8, 18.5, 35.0,
                          28.0, 6.5, 8.0, 7.5, 6.8,
                          13.0, 22.0, 20.0, 15.0, 28.0],
            "Min CGPA": [6.0, 6.0, 6.0, 7.0, 7.5,
                        7.0, 6.5, 6.5, 6.5, 6.0,
                        7.0, 7.0, 7.0, 6.5, 7.5],
            "Applications": [120, 95, 80, 45, 30, 35, 60, 50, 25, 30,
                            20, 15, 28, 22, 12],
        })

        fig = px.scatter(
            companies, x="Min CGPA", y="Avg Salary",
            size="Applications", color="Company",
            hover_name="Company",
            title="Company Landscape: CGPA vs Salary",
            labels={
                "Min CGPA": "Minimum CGPA Required",
                "Avg Salary": "Average Salary (LPA)"
            },
            template="plotly_white",
            size_max=40
        )
        fig.update_layout(height=450)
        return fig
