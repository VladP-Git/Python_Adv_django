from django.core.validators import MaxLengthValidator
from django.db import models

# Create your models here.
class Genre(models.TextChoices):
    HORROR = 'horror', 'Book Horror'
    LIRICS = 'lirics', 'Book Lirics'
    COMEDY = 'comedy', 'Book Comedy'

class Book(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    pub_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    genre = models.CharField(choices=Genre, default=Genre.COMEDY, max_length=100)
    author = models.ManyToManyField('Author', related_name='books')

    def __str__(self):
        return f'{self.title}; {self.price}'


class Author(models.Model):
    first_name = models.CharField(max_length=100, validators=[MaxLengthValidator(3)])
    last_name = models.CharField(max_length=100, validators=[MaxLengthValidator(3)])

    def __str__(self):
        return f'{self.first_name[0]}. {self.last_name}'