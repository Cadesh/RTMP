#!/bin/bash
# author: Andre Rosa
# OBEJECTIVE: creates a virtual environment named 'catenv' to run the server side
# To activate the virtual environment: source catenv/bin/activate
# then to run the code use: python main.py
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# INSTALL PYTHON3, IF NOT PRESENT
echo -e "\e[96mINSTALL PYTHON3\e[39m"
apt-get update
apt-get -y upgrade
apt install python3.7
apt-get install -y python3-pip
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
echo -e "\e[96mINSTALL PYTHON VIRTUAL ENV\e[39m"
#CREATE PYTHON ENVIRONMENT
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
echo -e "\e[96mCREATE PYTHON ENVIRONMENT\e[39m"
virtualenv --python=python3.7 catenv
source catenv/bin/activate
#INSTALL PYTHON MODULES
echo -e "\e[96mINSTALL PYTHON MODULES\e[39m"
pip install -r requirements.txt
echo -e "\e[96mActivate virtual env with: source catenv/bin/activate\e[39m"
# #---------------------------------------------------------------------------
# #---------------------------------------------------------------------------
