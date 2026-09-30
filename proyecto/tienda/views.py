from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ConsultaOllamaForm, ProductoForm
from .models import Producto
from .reportes import ejecutar_reportes
from .services.ollama_service import (
    MENSAJE_OLLAMA_CAIDO,
    OllamaNoDisponible,
    OllamaServiceFactory,
)


class CatalogoView(ListView):
    """Portada de la tienda: grilla de productos, no la tabla del inventario."""

    model = Producto
    template_name = "tienda/catalogo.html"
    context_object_name = "productos"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            # Misma busqueda que el inventario, para no tener dos criterios.
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(codigo__icontains=q)
                | Q(categoria__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/lista.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(codigo__icontains=q)
                | Q(categoria__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ProductoDetailView(DetailView):
    model = Producto
    template_name = "tienda/detalle.html"
    context_object_name = "producto"


class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/formulario.html"

    def form_valid(self, form):
        messages.success(self.request, "Producto creado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nuevo producto"
        ctx["accion"] = "Crear"
        return ctx


class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/formulario.html"

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nombre}"
        ctx["accion"] = "Guardar"
        return ctx


class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = "tienda/eliminar.html"
    context_object_name = "producto"
    success_url = reverse_lazy("tienda:lista")

    def form_valid(self, form):
        messages.success(self.request, "Producto eliminado.")
        return super().form_valid(form)


class ReportesView(TemplateView):
    template_name = "tienda/reportes.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["reportes"] = ejecutar_reportes(Producto.objects.all())
        return ctx


class ConsultaOllamaView(FormView):
    template_name = "tienda/consulta.html"
    form_class = ConsultaOllamaForm

    def form_valid(self, form):
        pregunta = form.cleaned_data["pregunta"]
        servicio = OllamaServiceFactory.crear()
        try:
            respuesta = servicio.responder(pregunta, Producto.objects.all())
        except OllamaNoDisponible:
            messages.error(self.request, MENSAJE_OLLAMA_CAIDO)
            return self.render_to_response(self.get_context_data(form=form))

        return self.render_to_response(
            self.get_context_data(
                form=ConsultaOllamaForm(),
                pregunta=pregunta,
                respuesta=respuesta,
            )
        )
