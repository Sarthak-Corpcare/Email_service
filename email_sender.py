from jinja2 import Environment, FileSystemLoader
import boto3
import os
from dotenv import load_dotenv
from db_connect import get_db_connection

#loading environment variable
load_dotenv()

# Fetching AWS credentials
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
source_email = os.getenv("SES_SOURCE_EMAIL")


# Amazon SES client
ses_client = boto3.client(
    "ses",
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
)

# Database connection
conn = get_db_connection()
cursor = conn.cursor()


def render_email_template(name, email):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("birthday_template.html")
    return template.render(name=name, email=email)


def send_email_ses(to_email, subject, html_content):
    response = ses_client.send_email(
        Source=source_email,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},

            "Body": {"Html": {"Data": html_content}},
        },
    )
    print("Email sent with Message ID:", response["MessageId"])


# Fetch users with birthdays today
cursor.execute("""
    SELECT id, name, email FROM clients 
    WHERE EXTRACT(MONTH FROM dob) = EXTRACT(MONTH FROM CURRENT_DATE) 
    AND EXTRACT(DAY FROM dob) = EXTRACT(DAY FROM CURRENT_DATE)
    AND (last_sent IS NULL OR last_sent < CURRENT_DATE);
""")
clients = cursor.fetchall()

for client in clients:
    client_id, name, email = client
    html_content = render_email_template(name, email)
    send_email_ses(email, "Happy Birthday!", html_content)

    #  last_sent to avoid duplicate emails
    cursor.execute("UPDATE clients SET last_sent = CURRENT_DATE WHERE id = %s;", (client_id,))
    conn.commit()

cursor.close()
conn.close()
