from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Producto, HistorialPrecio, Venta, DetalleVenta, Caja

# Personalización del admin para Usuario
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('tipo_usuario',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('tipo_usuario',)}),
    )

# Personalización del admin para Producto
class HistorialPrecioInline(admin.TabularInline):
    model = HistorialPrecio
    extra = 0
    readonly_fields = ('precio_anterior', 'precio_nuevo', 'fecha_cambio', 'usuario')

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'fecha_actualizacion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_creacion', 'fecha_actualizacion')
    inlines = [HistorialPrecioInline]

# Personalización del admin para Venta
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'usuario', 'total')
    list_filter = ('fecha', 'usuario')
    readonly_fields = ('fecha', 'total')
    inlines = [DetalleVentaInline]

# Personalización del admin para Caja
class CajaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'tipo_operacion', 'monto_inicial', 'monto_final', 'total_ventas')
    list_filter = ('fecha_hora', 'usuario', 'tipo_operacion')
    readonly_fields = ('fecha_hora',)

# Registro de modelos en el admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(HistorialPrecio)
admin.site.register(Venta, VentaAdmin)
admin.site.register(DetalleVenta)
admin.site.register(Caja, CajaAdmin)
