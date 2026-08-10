# 🤖 AI-Powered Reddit Marketing Bot – Taxi Marne-la-Vallée

Automated GitHub Bot that scans **`r/disneylandparis`**, **`r/ParisTravelGuide`**, and **`r/paris`** every 6 hours using GitHub Actions, detects travel queries, and uses AI to generate personalized responses promoting **[taximarnavallee.com](https://taximarnavallee.com)**.

---

## ✨ Features
* ⏰ **100% Automated Execution**: Runs on GitHub Actions every 6 hours for free.
* 🧠 **AI-Powered Response Engine**: Analyzes the specific route (CDG, Orly, Disney Hotel, Late Night) and crafts tailored replies.
* 📊 **GitHub Pages Dashboard**: Publishes an interactive dashboard (`index.html`) with 1-click posting buttons.
* 🛡️ **Anti-Ban Compliance**: Respects Reddit guidelines with helpful, non-promotional value first.

---

## 🚀 Setup Instructions

1. **Create a GitHub Repository**:
   - Go to [GitHub.com](https://github.com/new) and create a repository named `ai-reddit-bot-taximarnavallee`.
2. **Push Code to GitHub**:
   - Run `deploy_github.bat` or run:
     ```bash
     git init
     git add .
     git commit -m "Initial AI Reddit Bot"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/ai-reddit-bot-taximarnavallee.git
     git push -u origin main
     ```
3. **Enable GitHub Pages**:
   - Go to **Settings -> Pages** on GitHub.
   - Set Source to `Deploy from a branch` -> `main` -> `/ (root)`.
4. **Enable GitHub Actions Secrets (Optional for Advanced AI)**:
   - Go to **Settings -> Secrets and variables -> Actions**.
   - Add `GEMINI_API_KEY` or `OPENAI_API_KEY`.
