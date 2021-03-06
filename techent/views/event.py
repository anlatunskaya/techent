# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, url_for, render_template, make_response, abort
from techent.forms import EventForm, CommentForm, FileForm
from mongoengine.queryset import DoesNotExist
from techent.models import Event, Tag, Comment, User, DocumentFile
from sets import Set
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import datetime
import json
import mail
import requests
from werkzeug import secure_filename
from gridfs.errors import NoFile
from techent.extensions import *
from gridfs import GridFS
from mongoengine import *

event = Blueprint("event", __name__)

@event.route("/event", methods = ["GET", "POST"])
@login_required
def create_event():
    form = EventForm(request.form, csrf_enabled = False)
    if form.validate_on_submit():
        tags = []
        if form.tags.data:
            tags = form.tags.data.split(",")
            store_tag_metainformation(tags)

        start_date = form.iso_date(form.start_date.data)
        end_date = form.iso_date(form.end_date.data)
        user_id = current_user.id
        user = User.objects.with_id(ObjectId(user_id))
        attendees = [attendee.strip() for attendee in form.attendees.data.split(",")]
        event = Event(author=user,
                        subject = form.subject.data,
                        start_date = start_date,
                        end_date = end_date,
                        description = form.description.data,
                        hosts = form.hosts.data,
                        tags = tags,
                        attendees = attendees)
#        if request.files[form.logo.name]:
#            event.logo.put(request.files[form.logo.name])
        event.save()
        upload_logo(event.id)
        if str(event.attendees[0]) is not "":
            mail.send_event_invitation(event)
        return redirect(url_for("main.frontpage"))
    return render_template("create_event.html", form = form)

def store_tag_metainformation(tag_names):
    for tag_name in tag_names:
        try:
            tag = Tag.objects.get(name = tag_name)
        except DoesNotExist:
            tag = Tag(name = tag_name, count = 0, related_tags = [])

        #Increment count of posts on the tag
        tag.count += 1
        related_tags = Set(tag_names)
        related_tags.remove(tag_name)
        tag.related_tags = list(Set(tag.related_tags) | (related_tags))
        tag.save()
FS = None
@event.route('/upload-file/<event_id>', methods=['GET', 'POST'])
def upload_file(event_id):
    connection = mongoengine.connection
    db = connection.techent
    global FS
    if not FS:
        FS = GridFS(db)
    form = FileForm(request.form, csrf_enabled = False)
    if request.method == 'POST':
        file = request.files[form.file.name]
        if file:
            filename = file.filename
            oid = FS.put(file, content_type=file.content_type, filename=filename)
            event = Event.objects.with_id(ObjectId(event_id))
            document = DocumentFile(document_id=oid, name=filename, content_type=file.content_type)
            event.files.append(document)
            event.save()
    return redirect(url_for('event.show_event', event_id=event_id))

def upload_logo(event_id):
    connection = mongoengine.connection
    db = connection.techent
    global FS
    if not FS:
        FS = GridFS(db)
    form = EventForm(request.form, csrf_enabled = False)
    if request.method == 'POST':
        logo = request.files[form.logo.name]
        if logo:
            event = Event.objects.with_id(ObjectId(event_id))
            filename = logo.filename
            oid = FS.put(logo, content_type=logo.content_type, filename=filename)
            event.logo = DocumentFile(document_id=oid, name=filename, content_type=logo.content_type)
            event.save()
    return redirect(url_for('event.show_event', event_id=event_id))

@event.route('/create-event-in-calendar/<event_id>')
def create_event_in_calendar(event_id):
    event = Event.objects.with_id(event_id)
    user = User.objects.with_id(ObjectId(current_user.id))
    headers = {'Authorization': 'OAuth ' + str(current_user.access_token),
               'Content-Type': 'application/json'}
    data = {
            "summary": event.subject,
            "description": event.description,
            "reminders": [
                            {"method": "email", "minutes": 10}
                        ],
            "start": {"dateTime": str(event.start_date.isoformat()), "timeZone": "Europe/Kaliningrad"},
            "end": {"dateTime": str(event.end_date.isoformat()), "timeZone": "Europe/Kaliningrad"},
            "attendees": [
                        {"email": user.email}
                        ],
            "anyoneCanAddSelf": True,
            "guestsCanInviteOthers": True
    }
    data = str(json.dumps(data))
    req = requests.post('https://www.googleapis.com/calendar/v3/calendars/' + User.objects.with_id(ObjectId(current_user.id)).email + '/events', data=data, headers=headers)
    return redirect(url_for('event.show_event', event_id=event_id))

@event.route('/event/<event_id>')
def show_event(event_id):
    event = Event.objects.with_id(ObjectId(event_id))
    return render_template("show_event.html", event = event, current_user = current_user)

@event.route('/documents/<document_id>')
def download_document(document_id):
    try:
        file = FS.get(ObjectId(document_id))
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response
    except NoFile:
        abort(404)

@event.route('/event/<event_id>/comments', methods = ["POST"])
@login_required
def add_comment(event_id):
    form = CommentForm(request.form, csrf_enabled = False)
    event = Event.objects.with_id(event_id)
    if form.validate_on_submit():
        date = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        comment = Comment(text = form.comment.data, author = User.objects.with_id(ObjectId(current_user.id)), date = date)
        event.comments.append(comment)
        event.save()
    return redirect(url_for('event.show_event', event_id=event_id))

