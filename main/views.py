from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import RegisterForm
from .models import User, Artist, Music
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from datetime import date
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, "users/login.html")

    def post(self, request):
        if request.method == "POST":
            # Getting from post request
            email = request.POST["email"]
            password = request.POST["password"]

            # Checking if the user exists in database
            if User.objects.filter(email=email).exists():
                user = authenticate(email=email, password=password)
                # Checking if user is active or not
                if user is not None:
                    # Calling login function and redirect to home page
                    login(request, user)
                    messages.success(request, "Successfully loged in")
                    return redirect("dashboard")
                else:
                    messages.error(request, "Email or Password not matched!")
                    return redirect("login")
            else:
                messages.error(request, "Email does not exists!")
        else:
            print("This is not POST method")
        return render(request, "users/login.html")


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = make_password(form.cleaned_data['password'])
            email = form.cleaned_data['email']
            dob = form.cleaned_data["dob"]
            address = form.cleaned_data["address"]
            gender = form.cleaned_data["gender"]
            phone = form.cleaned_data["phone"]


            # Create a new user with a hashed password
            user = User.objects.create_user(first_name=first_name, last_name=last_name, dob=dob, 
                 password=password, email=email, address=address, gender=gender, phone=phone)
            messages.success(request, "user register successfully")
            user.save()
            return redirect("login")
        else:
            messages.warning(request, "something went wrong")
        return render(request, "users/register.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        try:
            logout(request)
            messages.success(request, "logout successfully")
            return redirect("login")
        except Exception:
            messages.error(
                "Something went wrong while logging out! Please try again and contact admin."
            )


class IndexView(View):
    def get(self, request):
        artists = Artist.objects.all().count()
        users = User.objects.all().count()
        musics = Music.objects.all().count()
        today = date.today()

        from django.db.models import Count

        artists_with_most_music = Artist.objects.annotate(num_music=Count('music')).order_by('-num_music')
        most_music_artist = artists_with_most_music.first()
        if most_music_artist:
            artist_name = most_music_artist.name
            number_of_music = most_music_artist.num_music
        else:
            artist_name = "No artist found"
            number_of_music = 0
        context = {
            "today": today,
            "users": users,
            "artists": artists,
            "musics": musics,
            "artists_musics": artist_name
        }
        return render(request, "seller_dashboard.html", context)


# users


class List_ProductView(LoginRequiredMixin, View):
    """
    class for listing all products from database.
    for access this class you must be logged in.
    :attributes login_url, redirect_field_name
    """

    login_url = "login"
    redirect_field_name = "inventory/dashboard"

    def get(self, request):
        """method for rendering product list and pagination
        parameters:
            request
        returns:
            template and context
        """
        brand = BrandForm()
        category = CategoryForm()
        products = Product.objects.all().order_by("-id")
        paginator = Paginator(products, 2)
        first_page = paginator.page(1).object_list
        page_range = paginator.page_range
        context = {
            "page_range": page_range,
            "products": first_page,
            "brands": brand,
            "category": category,
        }
        return render(request, "product/list.html", context)

    def post(self, request):
        products = Product.objects.all().order_by("-id")
        paginator = Paginator(products, 2)
        page_no = request.POST.get("page_no", None)
        results = list(
            paginator.page(page_no).object_list.values(
                "id",
                "name",
                "description",
                "cost_price",
                "selling_price",
                "brand__name",
                "quantity",
                "category__category",
                "subcategory__subcategory",
            )
        )
        return JsonResponse({"results": results})


class CreateView(View):
    # permission_required = ('product.add_product', 'product.change_product') add PermissionRequiredMixin
    def get(self, request, **kwargs):
        form = ProductForm()
        context = {"form": form}
        return render(request, "product/create.html", context)

    def post(self, request, **kwargs):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("list-product")
        else:
            messages.error(request, form.errors.as_data())
        context = {"form": form}
        return render(request, "product/create.html", context)


class Products_json(View):
    def get(self, request):
        data = Product.objects.all()
        brand = Brand.objects.all()
        subcat = Subcategory.objects.all()
        category = Category.objects.all()
        return JsonResponse(
            {
                "products": list(data.values()),
                "brands": list(brand.values()),
                "subcategory": list(subcat.values()),
                "category": list(category.values()),
            }
        )


class Delete_ProductView(View):
    permission_required = "product.delete_product"

    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        product.delete()
        messages.warning(request, f"{product.name} deleted")
        return redirect("list-product")


class Update_ProductView(View):
    def get(self, request, pk):
        data = Product.objects.get(id=pk)
        form = ProductForm(instance=data)
        context = {"form": form}
        return render(request, "product/update.html", context)

    def post(self, request, pk, **kwargs):
        form = ProductForm(request.POST)
        if form.is_valid():
            obj = Product.objects.get(id=pk)
            obj.name = form.cleaned_data["name"]
            obj.description = form.cleaned_data["description"]
            obj.cost_price = form.cleaned_data["cost_price"]
            obj.selling_price = form.cleaned_data["selling_price"]
            obj.brand = form.cleaned_data["brand"]
            obj.quantity = form.cleaned_data["quantity"]
            obj.category = form.cleaned_data["category"]
            obj.subcategory = form.cleaned_data["subcategory"]
            obj.save()
            messages.info(request, f"Product {obj.name} update successfully")
            return redirect("list-product")
        else:
            messages.error(request, form.errors.as_data())
        context = {"form": form}
        return render(request, "product/update.html", context, context)

