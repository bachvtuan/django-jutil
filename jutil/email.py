#pylint: disable=too-many-arguments,too-many-locals
import logging


logger = logging.getLogger(__name__)


def send_email(recipients: list, subject: str,  # noqa
               text: str = '', html: str = '',
               sender: str = '',
               files: list or None = None,
               cc_recipients: list or None = None,
               bcc_recipients: list or None = None,
               exceptions: bool = False):
    """
    Sends email using SendGrid API client. Requires settings EMAIL_SENDGRID_API_KEY to be set.
    :param recipients: List of "To" recipients. Single email (str); or comma-separated email list (str); or list of name-email pairs (e.g. settings.ADMINS)  # noqa
    :param subject: Subject of the email
    :param text: Body (text), optional
    :param html: Body (html), optional
    :param sender: Sender email, or settings.DEFAULT_FROM_EMAIL if missing
    :param files: Paths to files to attach
    :param cc_recipients: List of "Cc" recipients (if any). Single email (str); or comma-separated email list (str); or list of name-email pairs (e.g. settings.ADMINS)  # noqa
    :param bcc_recipients: List of "Bcc" recipients (if any). Single email (str); or comma-separated email list (str); or list of name-email pairs (e.g. settings.ADMINS)  # noqa
    :param exceptions: Raise exception if email sending fails. List of recipients; or single email (str); or comma-separated email list (str); or list of name-email pairs (e.g. settings.ADMINS)  # noqa
    :return: Status code 202 if emails were sent successfully
    """
    import sendgrid
    from sendgrid.helpers.mail import Content, Mail, Attachment
    from sendgrid import ClickTracking, FileType, FileName, TrackingSettings, Personalization
    from sendgrid import FileContent, ContentId, Disposition
    from django.conf import settings
    from base64 import b64encode
    from os.path import basename
    from django.utils.timezone import now
    from jutil.logs import log_event

    if files is None:
        files = []
    if cc_recipients is None:
        cc_recipients = []
    if bcc_recipients is None:
        bcc_recipients = []
    if isinstance(recipients, str):
        recipients = [str(r).strip() for r in recipients.split(',')]
    if isinstance(cc_recipients, str):
        cc_recipients = [str(r).strip() for r in cc_recipients.split(',')]
    if isinstance(bcc_recipients, str):
        bcc_recipients = [str(r).strip() for r in bcc_recipients.split(',')]

    try:
        # default sender to settings.DEFAULT_FROM_EMAIL
        if not sender:
            sender = settings.DEFAULT_FROM_EMAIL

        sg = sendgrid.SendGridAPIClient(api_key=settings.EMAIL_SENDGRID_API_KEY)
        from_email = sendgrid.Email(sender or settings.DEFAULT_FROM_EMAIL)
        text_content = Content('text/plain', text) if text else None
        html_content = Content('text/html', html) if html else None

        sg_email_list = []
        for recipient in recipients:
            sg_email_list.append(sendgrid.To())
        for recipient in cc_recipients:
            sg_email_list.append(sendgrid.Cc())
        for recipient in bcc_recipients:
            sg_email_list.append(sendgrid.Bcc())
        to_emails_data = list(recipients) + list(cc_recipients) + list(bcc_recipients)
        for ix, to_email in enumerate(sg_email_list):
            recipient = to_emails_data[ix]
            if isinstance(recipient, str):
                to_email.email = recipient
            elif isinstance(recipient, (list, tuple)) and len(recipient) == 2:
                to_email.name = recipient[0]
                to_email.email = recipient[1]
            else:
                raise Exception('Invalid recipient format: {}'.format(recipient))
        personalization = Personalization()
        for sg_email in sg_email_list:
            personalization.add_email(sg_email)

        mail = Mail(from_email=from_email, subject=subject, plain_text_content=text_content, html_content=html_content)
        mail.add_personalization(personalization)

        # stop SendGrid from replacing all links in the email
        mail.tracking_settings = TrackingSettings(click_tracking=ClickTracking(enable=False))

        for filename in files:
            with open(filename, 'rb') as fp:
                attachment = Attachment()
                attachment.file_type = FileType("application/octet-stream")
                attachment.file_name = FileName(basename(filename))
                attachment.file_content = FileContent(b64encode(fp.read()).decode())
                attachment.content_id = ContentId(basename(filename))
                attachment.disposition = Disposition("attachment")
                mail.add_attachment(attachment)

        send_time = now()
        res = sg.client.mail.send.post(request_body=mail.get())
        send_dt = (now() - send_time).total_seconds()

        if res.status_code == 202:
            log_event('EMAIL_SENT', data={'time': send_dt, 'to': recipients, 'subject': subject, 'status': res.status_code})
        else:
            log_event('EMAIL_ERROR', data={'time': send_dt, 'to': recipients, 'subject': subject, 'status': res.status_code, 'body': res.body})

    except Exception as e:
        logger.error(e)
        if exceptions:
            raise
        return -1

    return res.status_code
