from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("add/", views.product_create, name="add"),
    path("<int:pk>/", views.product_detail, name="detail"),
    path("<int:pk>/edit/", views.product_update, name="edit"),
    path("<int:pk>/delete/", views.product_delete, name="delete"),
    path("<int:pk>/items/add/", views.item_add, name="item_add"),
    path("items/<int:pk>/edit/", views.item_update, name="item_edit"),
    path("items/<int:pk>/delete/", views.item_delete, name="item_delete"),
]