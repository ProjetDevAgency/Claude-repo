@echo off
rem Lance le village : le serveur (relié à ton live TikTok) + une fenêtre Chrome où le son démarre tout seul.
cd /d "%~dp0"
if not exist node_modules call npm install
start "Village - serveur" cmd /k npm start
timeout /t 3 >nul
rem Chrome à part (profil dédié) avec la lecture automatique du son autorisée
start chrome --user-data-dir="%TEMP%\village-live" --autoplay-policy=no-user-gesture-required --app=http://localhost:3000 --window-size=540,960
