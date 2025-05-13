from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Modelo de Usuario personalizado
class Usuario(AbstractUser):
    ADMIN = 'admin'
    EMPLEADO = 'empleado'
    
    TIPO_USUARIO_CHOICES = [
        (ADMIN, 'Administrador'),
        (EMPLEADO, 'Empleado'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default=EMPLEADO,
        verbose_name='Tipo de Usuario'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

# Modelo de Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

# Modelo de Historial de Precios
class HistorialPrecio(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial_precios')
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Anterior')
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Nuevo')
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Cambio')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Usuario')
    
    def __str__(self):
        return f'{self.producto.nombre} - {self.fecha_cambio}'
    
    class Meta:
        verbose_name = 'Historial de Precio'
        verbose_name_plural = 'Historial de Precios'

# Modelo de Venta
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Usuario')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')
    
    def __str__(self):
        return f'Venta #{self.id} - {self.fecha}'
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

# Modelo de Detalle de Venta
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name='Producto')
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Unitario')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    
    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad}'
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

# Modelo de Caja
class Caja(models.Model):
    APERTURA = 'apertura'
    CIERRE = 'cierre'
    
    TIPO_OPERACION_CHOICES = [
        (APERTURA, 'Apertura de Caja'),
        (CIERRE, 'Cierre de Caja'),
    ]
    
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Usuario')
    tipo_operacion = models.CharField(max_length=10, choices=TIPO_OPERACION_CHOICES, verbose_name='Tipo de Operación')
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Monto Inicial')
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Monto Final')
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total Ventas')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    def __str__(self):
        return f'{self.get_tipo_operacion_display()} - {self.fecha_hora}'
    
    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
