from django.contrib import admin

from apps.library.models import Book, Author

admin.site.register(Author)

# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'pub_date')
    prepopulated_fields = {'slug': ('title',)}
