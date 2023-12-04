ls
cd
sudo nano tet
cd
ls
pwd
sudo apt-get install python3-venv -y
python3.10 -m venv env
sudo apt-get update
sudo apt-get install nginx postgresql certbot redis-server -y
sudo -u postgres psql -c "CREATE DATABASE ritual;"
sudo -u postgres psql -c "CREATE USER ritual_user_db WITH PASSWORD 'ritual_pPass_3276';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ritual TO ritual_user_db;"
source env/bin/activate
pip freeze -r req.txt 
locale -a
sudo locale-gen ru_RU.UTF-8
sudo update-locale LANG=ru_RU.UTF-8
locale
sudo update-locale LANG=ru_RU.UTF-8
locale
pip freeze -r req.txt
locale
sudo update-locale LANG=ru_RU.UTF-8
sudo locale-gen ru_RU.UTF-8
sudo update-locale LANG=ru_RU.UTF-8
locale
sudo reboot
adduser frontend
sudo adduser frontend
sudo passwd frontend
su
sudo mc
sudo apt install mc
sudo mc
ls
source env/bin/activate
python manage.py makemigrations
sudo systemctl restart gunicorn
python manage.py makemigrations
sudo systemctl restart gunicorn
sudo cerbot
sudo certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx
sudo systemctl reload nginx
sudo usermod -aG sudo frontend
sudo systemctl restart gunicorn
sudo chmod 755 "/etc/nginx/sites-available/site"
sudo chown www /etc/nginx/sites-available/site
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl restart gunicorn
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl restart gunicorn
ls
source env/bin/activate
pip install corsheaders
pip install django-cors-headers
sudo systemctl restart gunicorn
ls
source env/bin/activate
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart gunicorn
ls
source env/bin/activate
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart gunicorn
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart gunicorn
sudo systemctl restart gunicorn
source env/bin/activate
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart gunicorn
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart gunicorn
