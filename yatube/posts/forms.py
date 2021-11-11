from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('text'),
            'group': _('group'),
        }
        help_texts = {
            'group': _('Необязательно к заполнению'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('text')
        }
        help_texts = {
            'text': _('Оставьте комментарий'),
        }
