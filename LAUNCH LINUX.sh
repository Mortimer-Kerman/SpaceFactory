cd sources
if python main.py; then
    echo "Lancement du jeu - python"
else
    python3 main.py
    echo "Lancement du jeu - python3"
fi