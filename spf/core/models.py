from django.db import models


class Journal(models.Model):
    print_issn = models.CharField(max_length=9)
    online_issn = models.CharField(max_length=9)
    title = models.CharField(max_length=255)
    abbreviated_title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
