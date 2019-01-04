import re

from django.core import mail

def parse_search_string(search_string):
    tag_names = []
    find_value = ""
    tag_names = re.findall(r"\btag:(\w+)\b", search_string)
    find_value = re.sub(r"\btag:\w+\b", "", search_string)
    return tag_names, find_value.strip()


def set_filter_by_tag_names(queryset, names):
    for name in names:
        queryset = queryset.filter(tags__name=name)  
    return queryset


def new_answer_notify(email, url):
    subject = "New answer"
    message = url
    recipient_list = [email]
    mail.send_mail(
        subject,
        message,
        'from@example.com',
        recipient_list,
        fail_silently=True,
    )