import glob, json, os, shutil, smtplib

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_config import *

def initialize_message(sender_email, receivers_list):
    message = MIMEMultipart('related')
    message['From'] = sender_email
    message['To'] = ",".join(receivers_list)

    return message

def summarize_backups(soup):
    pattern = os.path.join(r"\\houdrsmb\Backup\DR\webgisdr\backups", "*-INCREMENTAL.webgissite")
    backups_list = glob.glob(pattern)
    backup_sizes_list = []
    backup_dates_list = []

    cutoff_date = datetime.now() - timedelta(90)
    recent_backups_list = []
    recent_backup_sizes_list = []
    old_backups_list = []
    old_backup_sizes_list = []
    for backup in backups_list:
        backup_size = os.path.getsize(backup) / (1024 ** 3)
        backup_sizes_list.append(backup_size)

        backup_date = datetime.fromtimestamp(os.path.getmtime(backup))
        backup_dates_list.append(backup_date)
        if backup_date >= cutoff_date:
            recent_backups_list.append(backup)
            recent_backup_sizes_list.append(backup_size)
        else:
            old_backups_list.append(backup)
            old_backup_sizes_list.append(backup_size)

    li_list = soup.find_all('li')
    li_list[0].append(f"{len(backups_list)} ({sum(backup_sizes_list):.3f} GB)")
    li_list[1].append(f"{len(recent_backups_list)} ({sum(recent_backup_sizes_list):.3f} GB)")
    li_list[2].append(f"{len(old_backups_list)} ({sum(old_backup_sizes_list):.3f} GB)")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(backup_dates_list, backup_sizes_list, marker='o')
    ax.set_xlabel("Date")
    ax.set_ylabel("Backup size (GB)")

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    ax.tick_params(axis='x', which='both', rotation=90)

    plt.tight_layout()
    fig.savefig("incremental.png")

def monitor_webgisdr(json_file, message):
    date_str = datetime.now().strftime("%Y%m%d")
    current_log = fr"\\houdrsmb\Backup\DR\webgisdr\logs\webgisdr-full-{date_str}.log.json"
    shutil.copy(webgisdr_log, current_log)

    with open(json_file, 'r') as j:
        data = json.load(j)
        status = data["status"]
        messages = data["messages"]
        duration = data["elapsedTime"]
        location = data["backupLocation"]
        results_list = data["results"]

    with open("alert_template.html", 'r', encoding='utf-8') as h:
        soup = BeautifulSoup(h, 'html.parser')

    h2 = soup.find('h2')
    if status == "success":
        message['Subject'] = "SUCCESS - Incremental WebGISDR Backup Monitoring - Dev-WMap-Houston"
        h2.string = "SUCCESS - Incremental WebGISDR Backup Monitoring - Dev-WMap-Houston"
    else:
        message['Subject'] = "FAILURE - Incremental WebGISDR Backup Monitoring - Dev-WMap-Houston"
        h2.string = "FAILURE - Incremental WebGISDR Backup Monitoring - Dev-WMap-Houston"

    tbody = soup.find('tbody')
    tr_list = tbody.find_all('tr')
    for index, tr in enumerate(tr_list):
        if index == 0:
            td = tr.find_all('td')
            td[1].string = status
            td[2].string = messages
            td[3].string = duration
        else:
            if len(results_list) > 0:
                td = tr.find_all('td')
                td[1].string = results_list[index - 1]["status"]
                td[2].string = results_list[index - 1]["messages"]
                td[3].string = results_list[index - 1]["elapsedTime"]
            else:
                pass

    if os.path.isfile(location):
        p_list = soup.find_all('p')
        p_list[0].append(location.replace("//", "/"))
        p_list[1].append(f"{os.path.getsize(location) / (1024 ** 3):.3f} GB")
        p_list[3].append(current_log)
    else:
        pass

    summarize_backups(soup)

    return soup

if __name__ == "__main__":
    webgisdr_log = r"\\houdrsmb\Backup\DR\webgisdr\logs\webgisdr-incremental.log.json"
    sender_email = SENDER_EMAIL
    receivers_list = RECEIVERS_LIST
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    smtp_username = SMTP_USERNAME
    smtp_password = SMTP_PASSWORD

    message = initialize_message(sender_email, receivers_list)
    soup = monitor_webgisdr(webgisdr_log, message)
    message.attach(MIMEText(str(soup), 'html'))

    with open("incremental.png", 'rb') as p:
        data = p.read()

    chart = MIMEImage(data, 'png')
    chart.add_header('Content-ID', "<chart>")
    chart.add_header('Content-Disposition', 'inline')
    message.attach(chart)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, receivers_list, message.as_string())

    with open("soup.html", 'w', encoding='utf-8') as h:
        h.write(str(soup))

    server.quit()
