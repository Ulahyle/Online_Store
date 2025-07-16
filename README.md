# Online Store

Welcome to the Online Store Backend repository.  
This repository contains all the code and exercises for building a multi-vendor e-commerce backend using Django and Django REST Framework.  
It is part of the mk bootCamp, aimed at teaching web development with Django through practical projects.

## Table of Contents

- About  
- Installation  
- Repository Structure  
- Usage  
- Contributing

## About

It contains the code for building the backend of a multi-vendor online store, focusing on:

- API development with Django REST Framework  
- Authentication using JWT  
- OTP-based login (via Redis)  
- Relational database design using PostgreSQL  
- Future integration with Docker, Redis, and Celery

## Installation

To get started with this project, follow these steps:

1. Clone the repository:
```bash
git clone git@github.com:Ulahyle/Online_Store.git
cd Online_Store

2. Create a virtual environment:
```bash
python -m venv .venv

3. Activate the virtual environment:

On Windows:

bash
Copy
Edit
venv\Scripts\activate
On macOS/Linux:

bash
Copy
Edit
source venv/bin/activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run migrations:

bash
Copy
Edit
python manage.py migrate
Start the development server:

bash
Copy
Edit
python manage.py runserver
Now open your browser and go to http://127.0.0.1:8000/ to view your Django API.

Repository Structure
bash
Copy
Edit
/Online_Store
├── config/                 # Main Django project settings
├── store/                  # Main app for products, stores, and carts
├── manage.py               # Django management script
├── requirements.txt        # Project dependencies
├── .gitignore              # Git ignore file
└── README.md               # This README file
Usage
Navigate to the relevant app or module to explore features.

Follow the code examples and model structures to practice Django skills.

Comments are provided in the code to help understand each component.

Contributing
If you would like to contribute to this repository, feel free to submit a pull request.

Steps:

Fork the repository

Create a new branch for your feature or bug fix

Make your changes

Submit a pull request
