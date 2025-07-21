from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta


class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=50)
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name) + " ["+str(self.isbn)+']'

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classroom = models.CharField(max_length=10)
    branch = models.CharField(max_length=10)
    roll_no = models.CharField(max_length=3, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    image = models.ImageField(upload_to="", blank=True)

    def __str__(self):
        return str(self.user) + " ["+str(self.branch)+']' + " ["+str(self.classroom)+']' + " ["+str(self.roll_no)+']'


def expiry():
    return datetime.today() + timedelta(days=14)

class IssuedBook(models.Model):
    student_id = models.CharField(max_length=100, blank=True) 
    isbn = models.CharField(max_length=13)
    issued_date = models.DateField()
    expiry_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='ISSUED')  # ISSUED, RETURNED, OVERDUE

    def save(self, *args, **kwargs):
        if not self.issued_date:
            self.issued_date = datetime.today().date()
        if not self.expiry_date:
            self.expiry_date = self.issued_date + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Book {self.isbn} issued to {self.student_id}"

class BookFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update book's average rating
        book = self.book
        total_ratings = BookFeedback.objects.filter(book=book).count()
        avg_rating = BookFeedback.objects.filter(book=book).aggregate(models.Avg('rating'))['rating__avg']
        book.total_ratings = total_ratings
        book.average_rating = avg_rating
        book.save()

    def __str__(self):
        return f"Feedback for {self.book.name} by {self.student.user.username}"
