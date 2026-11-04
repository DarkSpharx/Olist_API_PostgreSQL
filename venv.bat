@echo off
echo === 1. Creation de l'environnement virtuel (.venv) ===
python -m venv .venv

echo === 2. Activation de l'environnement ===
call .venv\Scripts\activate

echo === 3. Mise a jour de pip ===
python -m pip install --upgrade pip

echo === 4. Installation des bibliotheques ===
pip install jupyterlab pandas matplotlib scikit-learn pyarrow pathlib 

echo === Termine ! Tu peux fermer cette fenetre. ===
pause