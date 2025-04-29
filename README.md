# CS4340 - Software Maintenance - Group Project
Team Members: Anthony LaRiva and Craig Lillemon
Open Source under the MIT License (See LICENSE)

# Project Purpose:
This software extends an existing restaurant finder with dietary restrictions web application in order to modernize the application, apply corrective and perfective maintenance to existing features, and add new features that increase its usability and marketability.
Maintenance Features:
- RapidAPI update, Account System update.
Evolution Features:
- Favorites page, Ratings feature, AI powered Dish Ingr. feature.

# Project Setup:
Step 1:
Clone the GIThub repository to your local repository OR Download the software package as a .zip
Step 2:
Extract the .zip file into the desired file location on your machine.
Step 3:
Open a cmd prompt (LINUX) or powershell terminal (WINDOWS).
Step 4:
Navigate (with cd commands) into the 1st level of your project folder.
Step 5:
Navigate one level above your project folder, create a virtual environment, then activate the environment.
Step 6:
Navigate (with cd commands) out of your virtual environment to location: "your-project-name-here/restapp".
Step 6:
Execute the command: "pip install -r requirements.txt" to install all software dependencies.
Step 7 (Optional):
Execute the commands: "python manage.py makemigrations" and "python manage.py migrate" to create a local database for the application on your machine.
Step 8:
Execute the command: "$env:OPENAI_API_KEY = "input-your-openai-key-here"" (WINDOWS) or "export OPENAI_API_KEY="input-your-openapi-key-here"" (LINUX)
For the purpose of this course, our openai key key will be provided to Professor Moin via Canvas.
Step 9:
Execute the command: "python manage.py runserver" to initiate the development server.
Step 10:
Follow the link output to your terminal to access the development server on your preferred browser!

Disclaimer1: To continue development on this software, you are free to fork and extend it under the attached MIT License, but do not attempt committing changes to this fork or main.
Disclaimer2: In the event that RAPID API calls stop working as intended, visit "https://rapidapi.com/ptwebsolution/api/restaurants222" to create a free account and obtain a new key.
