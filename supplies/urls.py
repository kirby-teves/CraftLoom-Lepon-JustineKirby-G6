from django.urls import path

from . import views

app_name = "supplies"

urlpatterns = [
    path("", views.material_list, name="list"),
    path("add/", views.material_create, name="add"),
    path("<int:pk>/edit/", views.material_update, name="edit"),
    path("<int:pk>/delete/", views.material_delete, name="delete"),
    path("categories/", views.category_list, name="categories"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
]