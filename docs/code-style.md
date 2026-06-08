# Flask Best Practices

A simple `Flask` codebase that provides best practices for a secure production deployment.



## ✨ Code-base structure
The project has a super simple structure, represented as below:
```
< PROJECT ROOT >
   |
   |-- app/
   |    |
   |    |-- __init__.py                 # Initialization of app
   |    |-- config.py                   # Handlers for the front end routes
   |    |-- setup_security.py                      
   |    |-- auth/
   |    |
   |    |   |-- __init__.py
   |    |   |-- email.py
   |    |   |-- forms.py
   |    |   |-- models.py               # Database models for storing data
   |    |   |-- routes.py               # REST API hanlder
   |    |
   |    |-- static/                     # CSS files, Javascripts files
   |    |   
   |    |   |-- css/
   |    |   |
   |    |   |   |-- bootstrap.min.css
   |    |   |   |-- bootstrap.min.css.map
   |    |   |   |-- style.css
   |    |   |
   |    |   |-- js/
   |    |   |
   |    |   |   |-- bootstrap.min.js
   |    |   |   |-- jquery.min.js
   |    |   |
   |    |-- templates/
   |    |
   |    |    |-- auth/                    # Auth related pages login/register
   |    |    |
   |    |    |    |-- login.html
   |    |    |    |-- register.html
   |    |    |    |-- reset_password.html
   |    |    |    |-- reset_password_request.html
   |    |    |
   |    |    |-- bootstrap/
   |    |    |
   |    |    |    |-- bs5_base.html
   |    |    |
   |    |    |-- email/
   |    |    |  
   |    |    |    |-- reset_password.html
   |    |    |    |-- reset_password.txt
   |    |    |
   |    |    |-- forms/
   |    |    |
   |    |    |    |-- forms.html
   |    |    |
   |    |    |-- navbar/
   |    |    |  
   |    |    |    |-- messages.html
   |    |    |    |-- navbar.html
   |    |    |-- base.html
   |    |
   |    |-- utils/
   |    |
   |    |    |-- __init__.py
   |    |    |-- app_logger.py
   |    |    |-- decorators.py
   |    |    |-- mailer.py
   |    |
   |-- requirements.txt
   |-- run.py
   |
   |-- ************************************************************************
```
