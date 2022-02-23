call conda remove -y -n installer --all
call conda create -y --name installer python=3.7
call conda activate installer
call pip install -r requirements.txt
call pyinstaller -F main.py
call conda deactivate installer