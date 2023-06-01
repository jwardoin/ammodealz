import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets

class Post:
    def __init__(self, title, timeElapsed, url):
        self.title = title
        self.timeElapsed = timeElapsed
        self.url = url

    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__, sort_keys=True, indent=4)


def extract_links(page_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://www.reddit.com/r/gundeals/new/?f=flair_name%3A\"Ammo\"" # Replace 'subreddit_name' with your subreddit name
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', {'class': '_32pB7ODBwG3OSx1u_17g58'})
    links = []
    for post in posts:
        title = post.find('h3', { 'class': '_eYtD2XCVieq6emjKBH3m'}).text
        timeElapsed = post.find('span', {'class': '_2VF2J19pUIMSLJFky-7PEI'}).text
        url = post.find('a', {'_13svhQIUZqD9PVzFcLwOKT styled-outbound-link'})['href']
        link = Post(title, timeElapsed, url)
        # links.append(link) # for testing only
        if timeElapsed.__contains__('minutes'):
            if timeElapsed[0] <= 5 and timeElapsed[1] == ' ':
                links.append(link)
        if timeElapsed.__contains__('seconds') or timeElapsed.__contains__('just now'):
            links.append(link)
    return links

def send_email(links):
    if len(links) > 0:
        reddit_email_content = ''
        for link in links:
            reddit_email_content += link.title + '<br>' + link.url + '<br><br>'
        
        # Email Details
        fromaddr = secrets.SENDER_EMAIL
        toaddr = secrets.RECEIVER_EMAIL
        password = secrets.SENDER_PASSWORD

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Ammo Dealz"

        body = "Here are your ammo deals, sir\n" + reddit_email_content
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(fromaddr, password)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()   
    
links = extract_links('https://www.reddit.com/r/gundeals/new/?f=flair_name%3A\"Ammo\"')
send_email(links)

