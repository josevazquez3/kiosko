from django.urls import path, re_path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Redirect for Django's default auth URLs
    re_path(r'^accounts/login/.*$', RedirectView.as_view(pattern_name='login', permanent=False)),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Usuarios
path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
path('usuarios/registro/', views.registro_usuario, name='registro_usuario'),
path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
path('usuarios/<int:pk>/desactivar/', views.desactivar_usuario, name='desactivar_usuario'),
path('usuarios/<int:pk>/activar/', views.activar_usuario, name='activar_usuario'),
path('usuarios/<int:pk>/eliminar/', views.confirmar_eliminar_usuario, name='confirmar_eliminar_usuario'),
    
    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    
    # Ventas
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/nueva/', views.nueva_venta, name='nueva_venta'),
    path('ventas/<int:venta_id>/detalle/', views.detalle_venta, name='detalle_venta'),
    path('ventas/<int:venta_id>/agregar-detalle/', views.agregar_detalle_venta, name='agregar_detalle_venta'),
    path('ventas/<int:venta_id>/finalizar/', views.finalizar_venta, name='finalizar_venta'),
    
    # Caja
    path('caja/apertura/', views.apertura_caja, name='apertura_caja'),
    path('caja/cierre/', views.cierre_caja, name='cierre_caja'),
    path('caja/historial/', views.historial_caja, name='historial_caja'),
]