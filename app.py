import pandas as pd
import re
from flask import Flask, render_template
import os
import sys

app = Flask(__name__)

csv_dir = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\CSV"
csv_files = [file for file in os.listdir(csv_dir) if file.endswith(".csv")]

def remove_column_from_csv_files(csv_dir):
    files = os.listdir(csv_dir)
    for filename in files:
        if filename.endswith(".csv"):
            file_path = os.path.join(csv_dir, filename)
            df = pd.read_csv(file_path, escapechar='\\')
            if 'ContainerLog' in df.columns:
                columns_to_remove = ['Version','Qualifiers','Level','Task','Keywords','Opcode','ContainerLog', 'Bookmark', 'KeywordsDisplayNames', 'Properties', 'RelatedActivityId', 'ActivityId','MatchedQueryIds']
                df.drop(columns=columns_to_remove, inplace=True)
                df.to_csv(file_path, index=False)

remove_column_from_csv_files(csv_dir)

def process_dataframe(df):
    df.replace(to_replace=r'\n', value="<br>", regex=True, inplace=True)
    df.replace(to_replace=r'\r', value="", regex=True, inplace=True)
    df.replace(to_replace=r'\t', value="    ", regex=True, inplace=True)

def find_http_https_requests_and_ips(df, column_name):
    unique_urls = set()
    unique_ips = set()
    url_regex = r'https?://\S+'
    ip_regex = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(:[0-9]+)?'

    if column_name in df.columns:
        messages = df[column_name].astype(str)
        for message in messages:
            urls = re.findall(url_regex, message)
            for url in urls:
                unique_urls.add(url)
                ip_match = re.search(ip_regex, url)
                if ip_match:
                    unique_ips.add(ip_match.group())

    return unique_urls, unique_ips

def write_ips_to_csv(ips, filename="network_map.csv"):
    df = pd.DataFrame(ips, columns=["IP"])
    df.to_csv(os.path.join(csv_dir, filename), index=False)

@app.route("/")
def index():
    data_frames = []
    unique_http_requests = set()
    all_unique_ips = set()

    for file in csv_files:
        file_path = os.path.join(csv_dir, file)
        try:
            df = pd.read_csv(file_path)
            process_dataframe(df)
            urls, ips = find_http_https_requests_and_ips(df, 'Message')
            unique_http_requests.update(urls)
            all_unique_ips.update(ips)
            html_table = df.to_html(classes="table table-striped", index=False, escape=False)
            data_frames.append((file, html_table))
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
    
    return render_template("index.html", data_frames=data_frames, unique_http_requests=unique_http_requests)

if __name__ == "__main__":
    app.run(port=8080)