from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

@app.route("/")
def index():
    return redirect(url_for('project.index'))