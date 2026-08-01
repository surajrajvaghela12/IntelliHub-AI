# IntelliHub AI - Claude AI Presentation (PPT) Workflow & Master Prompt

This document provides a **complete, step-by-step workflow** and a **Master Prompt** to generate a presentation deck (PPT) using Claude AI, Gamma, or Microsoft PowerPoint.

---

## 🚀 Part 1: How to Use This Workflow with Claude AI

1. Open **[Claude AI](https://claude.ai)** in your browser.
2. Copy the **Master Prompt** below (Part 2) completely.
3. Paste the prompt into Claude AI.
4. Claude AI will generate a complete slide-by-slide text presentation structure, speaker notes, and design guidelines.
5. *(Optional)* Copy Claude AI's generated response into **[Gamma App](https://gamma.app)** or **Microsoft PowerPoint (Copilot)** to auto-generate a downloadable `.pptx` presentation file instantly!

---

## 📑 Part 2: Master Copy-Paste Prompt for Claude AI

```text
Act as a Senior AI Architect and Executive SaaS Product Manager. 

I need a complete 12-Slide Presentation Deck for a project presentation on "IntelliHub AI - Data Analytics, Machine Learning & Deep Learning SaaS Platform".

Please generate a professional, slide-by-slide presentation deck. For each slide, provide:
- Slide Title
- Subtitle
- Visual / Icon Suggestions
- Key Bullet Points (concise & high impact)
- Speaker Notes

Here is the exact project background and architecture:
Project Name: IntelliHub AI
Developer: Surajraj Vaghela (GitHub: surajrajvaghela12)
Core Concept: All-in-one AI & ML Platform empowering data scientists, researchers, and students to upload datasets, clean data, run EDA, train ML/DL models with AutoML, scrape web data, chat with an AI assistant, and generate automated PDF reports.

SaaS Platform Modules:
1. Interactive Dashboard: High-level metrics, dataset counts, trained models, storage metrics, quick action cards.
2. Dataset Manager: Dataset upload (CSV, Excel, JSON), automated schema inspection, row/column/memory metadata analysis, dataset versioning (v1, v2, v3).
3. AI Data Cleaner: Automated & manual cleaning (drop nulls, mean/median/mode imputation, IQR/Z-score outlier removal, One-Hot/Label encoding, scaling). Saves cleaned dataset as new version.
4. Exploratory EDA Engine: Interactive Seaborn/Plotly correlation heatmaps, AI correlation explanations, NetworkX feature relationship graphs with node degree centrality, 2-way cross-tabulations (pd.crosstab), and 12+ custom charts.
5. ML Studio & AutoML Leaderboard: Automated task detection (Regression vs Classification), algorithm selection (Random Forest, Decision Tree, Polynomial Regression, KNN, Logistic Regression), hyperparameter evaluation, model performance metrics, user-specific Model Leaderboard ranking, and real-time inference prediction.
6. Deep Learning Studio: PyTorch neural network training, dynamic architecture specification (layers, activation functions, learning rates, epochs), training loss visualization, and epoch history.
7. Universal Web Scraper: Multi-strategy web data extraction from any URL (HTML tables, direct CSV links, JSON data feeds, card grids, page content) with 1-click dataset manager ingestion.
8. AI Analyst Assistant & PDF Report Generator: Context-aware conversational AI chatbot and 1-click automated PDF executive summary generator (ReportLab).
9. SaaS Security & Multi-Role Governance: Role-based permissions (Student 5-dataset limit vs Researcher/Admin unlimited), User authentication, signals for profile management, and Admin control panel.

Tech Stack: Django 5, Python 3.11, Pandas, NumPy, Scikit-Learn, PyTorch, BeautifulSoup4, NetworkX, Plotly, ReportLab, Bootstrap 5, Glassmorphic UI.

Generate the 12 slides now with clean formatting ready for PPT creation.
```

---

## 🎨 Part 3: Detailed Slide Structure Overview

| Slide # | Title | Key Contents |
|---|---|---|
| **Slide 1** | Cover / Title | Project Name, Subtitle, Developer Name (`surajrajvaghela12`), Date |
| **Slide 2** | Problem Statement | Data fragmentation, complex ML setup code, lack of accessible GUI for EDA & AutoML |
| **Slide 3** | The Solution: IntelliHub AI | End-to-end web-based SaaS platform simplifying data engineering to model deployment |
| **Slide 4** | Intelligent Dataset Manager | Versioning system (v1, v2), metadata profiling (rows, cols, nulls, duplicates) |
| **Slide 5** | AI Automated Data Cleaner | Imputation, outlier removal (IQR/Z-score), encoding, version comparison |
| **Slide 6** | Exploratory EDA & NetworkX | Correlation matrix, NetworkX feature graphs, node degree centrality, crosstabs |
| **Slide 7** | ML Studio & Model Leaderboard | Regression/Classification algorithms, AutoML, user model rankings |
| **Slide 8** | Deep Learning Studio (PyTorch) | Custom neural network building, epoch loss curves, real-time predictions |
| **Slide 9** | Universal Web Scraper | Scraping any web link (CSV, JSON, HTML tables), direct ingestion into Dataset Manager |
| **Slide 10** | AI Analyst & Report Generator | Conversational assistant, 1-click executive PDF report generation |
| **Slide 11** | Technology Stack & Security | Django, Scikit-Learn, PyTorch, Plotly, Role-based governance (Student vs Admin) |
| **Slide 12** | Conclusion & GitHub Repo | Summary, GitHub Repository (`surajrajvaghela12/IntelliHub-AI`), Live Deployment Link |
