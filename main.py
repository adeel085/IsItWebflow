from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def submit():
    website_url = request.form['websiteUrl']
    if is_it_webflow(website_url):
        return "Yes, it's built in webflow"
    else:
        return "No, it's not built in webflow"


def is_it_webflow(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    is_webflow = False
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            print("404 page not found.")
            exit()

        soup = BeautifulSoup(response.content, "html.parser")
        html_tag = soup.find("html")

        if html_tag.has_attr("data-wf-page") and html_tag.has_attr("data-wf-site"):
            is_webflow = True
        else:
            print("Please wait. It can take a few minutes...")
            for script_tag in soup.findAll("script"):
                if script_tag.has_attr("src"):
                    src = script_tag["src"]
                    src_ok = False

                    if not src.startswith(url):
                        if src.startswith("//"):
                            src = "http:" + src
                        elif src.startswith("/"):
                            src = url + src
                        else:
                            src = url + "/" + src

                    if src.startswith("http:") or src.startswith("https:"):
                        src_ok = True
                    elif src.startswith("//"):
                        src = "https:" + src
                        src_ok = True

                    if not src_ok:
                        continue

                    response = requests.get(src, headers=headers)

                    if response.status_code == 404:
                        continue

                    js_code = response.text
                    if "window.Webflow" in js_code:
                        is_webflow = True
                        break

        return is_webflow
    except requests.exceptions.RequestException as e:
        return is_webflow


# app.run(host='localhost', port=3000)
