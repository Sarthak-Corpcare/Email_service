This project is a Python-based email automation service that sends birthday greetings to users stored in a PostgreSQL database. It utilizes Amazon SES (Simple Email Service) for email delivery and Jinja2 for HTML templating.

Features :
Fetches users with birthdays on the current date.
Sends personalized HTML email greetings via Amazon SES.
Ensures emails are not sent multiple times by updating the last_sent field in the database.
Uses environment variables for secure AWS credentials handling.
