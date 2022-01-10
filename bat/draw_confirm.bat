@echo off
set PYTHONUNBUFFERED=1
set DB_USER=postgres
set DB_PASSWORD=00620513
set DJANGO_SETTINGS_MODULE=toei_court.settings_dev
cd C:\Users\TOSHIBA\Desktop\Django_App\venv_toei_court\Scripts\
python C:\Users\TOSHIBA\Desktop\Django_App\venv_toei_court\toei_court\manage.py draw_confirm
Pause