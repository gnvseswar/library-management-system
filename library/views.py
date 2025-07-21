from library.forms import IssueBookForm, ReturnBookForm, BookFeedbackForm
from django.shortcuts import redirect, render,HttpResponse
from .models import *
from .forms import IssueBookForm
from django.contrib.auth import authenticate, login, logout
from . import forms, models
from datetime import date, timedelta, datetime
from django.contrib.auth.decorators import login_required
from .models import IssuedBook  
from django.contrib import messages


def index(request):
    return render(request, "index.html")

@login_required(login_url = '/admin_login')
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']

        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category)
        books.save()
        alert = True
        return render(request, "add_book.html", {'alert':alert})
    return render(request, "add_book.html")

@login_required(login_url = '/admin_login')
def view_books(request):
    books = Book.objects.all()
    return render(request, "view_books.html", {'books':books})

@login_required(login_url = '/student_login')
def student_view_books(request):
    books = Book.objects.all()
    return render(request, "student_view_books.html", {'books':books})

@login_required(login_url = '/admin_login')
def view_students(request):
    students = Student.objects.all()
    return render(request, "view_students.html", {'students':students})

@login_required(login_url = '/admin_login')
def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student_id = request.POST['name2']
            obj.isbn = request.POST['isbn2']
            obj.issued_date = form.cleaned_data['issue_date']
            # Calculate expiry date as 14 days from issue date
            obj.expiry_date = obj.issued_date + timedelta(days=14)
            obj.save()
            alert = True
            return render(request, "issue_book.html", {'obj':obj, 'alert':alert})
    else:
        # Calculate initial expiry date for display
        initial_expiry = date.today() + timedelta(days=14)
        return render(request, "issue_book.html", {'form':form, 'initial_expiry':initial_expiry})

@login_required(login_url = '/admin_login')
def view_issued_book(request):
    issuedBooks = IssuedBook.objects.all()
    details = []
    for issued_book in issuedBooks:
        days = (date.today()-issued_book.issued_date)
        d=days.days
        fine=0
        if d>14 and not issued_book.return_date:
            day=d-14
            fine=day*5
        
        books = list(models.Book.objects.filter(isbn=issued_book.isbn))
        students = list(models.Student.objects.filter(user=issued_book.student_id))
        
        # Check if feedback exists
        feedback = None
        if books and students:
            feedback = BookFeedback.objects.filter(
                book=books[0],
                student=students[0]
            ).first()
        
        i=0
        for l in books:
            t=(
                students[i].user,
                students[i].user_id,
                books[i].name,
                books[i].isbn,
                issued_book.issued_date,
                issued_book.expiry_date,
                issued_book.return_date,
                fine if not issued_book.return_date else issued_book.fine_amount,
                issued_book.status,
                feedback.rating if feedback else None,
                feedback.feedback if feedback else None,
                issued_book.id
            )
            i=i+1
            details.append(t)
    return render(request, "view_issued_book.html", {'issuedBooks':issuedBooks, 'details':details})

@login_required(login_url = '/student_login')
def student_issued_books(request):
    student = Student.objects.filter(user_id=request.user.id)
    issuedBooks = IssuedBook.objects.filter(student_id=student[0].user_id)
    details = []

    for i in issuedBooks:
        books = Book.objects.filter(isbn=i.isbn)
        for book in books:
            days = (date.today()-i.issued_date)
            d = days.days
            fine = 0
            if d>15:
                day = d-14
                fine = day*5
            
            # Check if feedback exists for this book
            feedback_exists = BookFeedback.objects.filter(book=book, student=student[0]).exists()
            
            t = (
                request.user.id,
                request.user.get_full_name,
                book.name,
                book.author,
                i.issued_date,
                i.expiry_date,
                i.return_date,
                fine,
                i.status,
                i.id,
                feedback_exists  # Add feedback status
            )
            details.append(t)
    return render(request,'student_issued_books.html',{'details':details})

@login_required(login_url = '/student_login')
def profile(request):
    return render(request, "profile.html")

@login_required(login_url = '/student_login')
def edit_profile(request):
    student = Student.objects.get(user=request.user)
    if request.method == "POST":
        email = request.POST['email']
        phone = request.POST['phone']
        branch = request.POST['branch']
        classroom = request.POST['classroom']
        roll_no = request.POST['roll_no']

        student.user.email = email
        student.phone = phone
        student.branch = branch
        student.classroom = classroom
        student.roll_no = roll_no
        student.user.save()
        student.save()
        alert = True
        return render(request, "edit_profile.html", {'alert':alert})
    return render(request, "edit_profile.html")

def delete_book(request, myid):
    books = Book.objects.filter(id=myid)
    books.delete()
    return redirect("/view_books")

def delete_issue(request, myid):
    issued_book = IssuedBook.objects.filter(id=myid)
    issued_book.delete()
    return redirect("/view_issued_book")

def delete_student(request, myid):
    students = Student.objects.filter(id=myid)
    students.delete()
    return redirect("/view_students")

def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html")

def student_registration(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        branch = request.POST['branch']
        classroom = request.POST['classroom']
        roll_no = request.POST['roll_no']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, "student_registration.html", {'passnotmatch': True})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "student_registration.html", {'username_exists': True})

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create student profile
            student = Student.objects.create(
                user=user,
                phone=phone,
                branch=branch,
                classroom=classroom,
                roll_no=roll_no,
                image=image
            )
            
            return render(request, "student_registration.html", {'success': True})
            
        except Exception as e:
            # If anything fails, clean up
            if 'user' in locals():
                user.delete()
            return render(request, "student_registration.html", {'error': True})
            
    return render(request, "student_registration.html")

def student_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return HttpResponse("Invalid Password or Username`")
            else:
                return redirect("/profile")
        else:
            alert = True
            return render(request, "student_login.html", {'alert':alert})
    return render(request, "student_login.html")

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("/view_students")  #add the new admin home page here
            else:
                return HttpResponse("Invalid Password or Username")
        else:
            alert = True
            return render(request, "admin_login.html", {'alert':alert})
    return render(request, "admin_login.html")

def Logout(request):
    logout(request)
    return redirect ("/")

@login_required(login_url='/student_login')
def return_book(request, issue_id):
    issued_book = IssuedBook.objects.get(id=issue_id)
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            return_date = form.cleaned_data['return_date']
            issued_book.return_date = return_date
            issued_book.status = 'RETURNED'
            
            # Calculate fine if overdue
            if return_date > issued_book.expiry_date:
                days_overdue = (return_date - issued_book.expiry_date).days
                issued_book.fine_amount = days_overdue * 5  # ₹5 per day fine
            
            issued_book.save()
            messages.success(request, 'Book returned successfully!')
            return redirect('student_issued_books')
    else:
        form = ReturnBookForm()
    
    return render(request, 'return_book.html', {'form': form, 'issued_book': issued_book})

@login_required(login_url='/student_login')
def submit_feedback(request, issue_id):
    issued_book = IssuedBook.objects.get(id=issue_id)
    book = Book.objects.get(isbn=issued_book.isbn)
    student = Student.objects.get(user_id=request.user.id)
    
    # Check if feedback already exists
    existing_feedback = BookFeedback.objects.filter(book=book, student=student).exists()
    if existing_feedback:
        messages.warning(request, 'You have already submitted feedback for this book.')
        return redirect('student_issued_books')
    
    if request.method == 'POST':
        form = BookFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.book = book
            feedback.student = student
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('student_issued_books')
    else:
        form = BookFeedbackForm()
    
    return render(request, 'submit_feedback.html', {
        'form': form,
        'book': book,
        'issued_book': issued_book
    })