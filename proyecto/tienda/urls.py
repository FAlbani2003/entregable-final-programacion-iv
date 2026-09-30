from django.urls import path

from . import views

app_name = "tienda"

urlpatterns = [
    path("", views.ProductoListView.as_view(), name="lista"),
    path("catalogo/", views.CatalogoView.as_view(), name="catalogo"),
    path("reportes/", views.ReportesView.as_view(), name="reportes"),
    path("consulta/", views.ConsultaOllamaView.as_view(), name="consulta"),
    path("nuevo/", views.ProductoCreateView.as_view(), name="crear"),
    path("<int:pk>/", views.ProductoDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.ProductoDeleteView.as_view(), name="eliminar"),
]
