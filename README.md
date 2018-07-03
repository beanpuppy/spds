# spds
source code for spds

## Setting up on a development environment 
```
# Clone it
git clone https://github.com/apt-helion/spds
cd spds

# Using the python virtual environment module (venv), create a python
# environment into "./env"
python3.6 -m venv env

# Setup your shell for this project
source env/bin/activate

# Install requirements for this project
pip install -r requirements.txt

# Set environment variable
export FLASK_ENV=development

# Copy example_config.py to config.py then edit it
cp example_config.py config.py
vim config.py

# Now you should source 'spds.sql' into your database

# Start the server
flask run
```

You should be able to view it on `127.0.0.1:5000`.

If you want you can set up your `/etc/hosts` to give it a hostname e.g:
```
# /etc/hosts

# address           hostname

127.0.0.1:5000      spds.com
```
Now you can access it through `spds.com`.
