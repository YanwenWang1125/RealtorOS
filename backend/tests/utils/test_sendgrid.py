import os
import pytest
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()


@pytest.mark.skipif(
    not os.environ.get('SENDGRID_API_KEY'),
    reason="SENDGRID_API_KEY not set"
)
def test_sendgrid_email():
    """Test sending email via SendGrid (requires SENDGRID_API_KEY)"""
    message = Mail(
        from_email='yanwenwang1125@gmail.com',
        to_emails='leowong228@gmail.com',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        # sg.set_sendgrid_data_residency("eu")
        # uncomment the above line if you are sending mail using a regional EU subuser
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        assert response.status_code in [200, 201, 202]
    except Exception as e:
        print(str(e))
        raise