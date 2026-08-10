@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================================
echo   INITIALISATION & PUBLICATION DU BOT AI REDDIT GITHUB
echo ==========================================================
echo.
git init
git add .
git commit -m "Initialisation Bot IA Reddit Taxi Marne-la-Vallee"
git branch -M main
echo.
echo ==========================================================
echo  Pour publier sur GitHub, creez un depot sur GitHub.com, 
echo  puis collez l'URL de votre depot ci-dessous.
echo ==========================================================
echo.
set /p REPO_URL="Entrez l'URL de votre depot GitHub (ex: https://github.com/votre-nom/ai-reddit-bot.git) : "

if not "%REPO_URL%"=="" (
    git remote add origin %REPO_URL%
    git push -u origin main
    echo.
    echo ==========================================================
    echo  BOT IA PUBLIE SUR GITHUB AVEC SUCCES !
    echo ==========================================================
)
pause
