from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Message


def contact():
    if request.method == 'POST':        
        message['name'] = request.form['name']
        message['email'] = request.form['email']
        message['subject'] = request.form['subject']
        message['message'] = request.form['message']

        send_message(message)
        return redirect(url_for('index'))    

    return redirect(url_for('index'))


def send_message(message):

    msg = Message(message.get('subject'), sender = message.get('email'),
            recipients = [app.config['MAIL_USERNAME']],
            body= message.get('message')
    )  
    mail.send(msg)