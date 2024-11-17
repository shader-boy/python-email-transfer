from dotenv import load_dotenv
import imaplib
import email
import os
from bs4 import BeautifulSoup

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


def connect_to_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail


def decode_content(content, charset):
    try:
        return content.decode(charset or "utf-8")
    except (UnicodeDecodeError, AttributeError):
        return content.decode("utf-8", errors="replace")


def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = [
        link["href"]
        for link in soup.find_all("a", href=True)
        if "spotify" in link["href"].lower()
    ]
    return links


def search_for_email():
    mail = connect_to_mail()
    _, search_data = mail.search(None, '(BODY "Spotify")')
    data = search_data[0].split()

    links = []

    for num in data:
        _, data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                charset = part.get_content_charset()
                if part.get_content_type() == "text/html":
                    html_content = decode_content(
                        part.get_payload(decode=True), charset
                    )
                    links.extend(extract_links_from_html(html_content))

        else:
            content_type = msg.get_content_type()
            charset = msg.get_content_charset()
            content = decode_content(msg.get_payload(decode=True), charset)

            if content_type == "text/html":
                links.extend(extract_links_from_html(content))

    mail.logout()
    return links


search_for_email()
