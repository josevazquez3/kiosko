from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.utils import timezone
from .models import Usuario, Producto, HistorialPrecio, Venta, DetalleVenta, Caja
from .forms import (
    LoginForm, RegistroUsuarioForm, ProductoForm, 
    VentaForm, DetalleVentaForm, AperturaCajaForm, CierreCajaForm
)

# Vistas de autenticación
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'kiosco_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def registro_usuario(request):
    # Solo administradores pueden registrar usuarios
    if request.user.tipo_usuario != Usuario.ADMIN:
        messages.error(request, 'No tienes permisos para registrar usuarios')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente')
            return redirect('lista_usuarios')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'kiosco_app/registro_usuario.html', {'form': form})

@login_required
def lista_usuarios(request):
    # Solo administradores pueden ver la lista de usuarios
    if request.user.tipo_usuario != Usuario.ADMIN:
        messages.error(request, 'No tienes permisos para ver la lista de usuarios')
        return redirect('dashboard')
    
    # Obtener todos los usuarios
    usuarios = Usuario.objects.all()
    
    # Filtrar por búsqueda (nombre de usuario, nombre o apellido)
    search_query = request.GET.get('search', '')
    if search_query:
        usuarios = usuarios.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filtrar por tipo de usuario
    tipo_usuario = request.GET.get('tipo', '')
    if tipo_usuario:
        usuarios = usuarios.filter(tipo_usuario=tipo_usuario)
    
    # Filtrar por estado (activo/inactivo)
    estado = request.GET.get('estado', '')
    if estado == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    # Ordenar por nombre de usuario
    usuarios = usuarios.order_by('username')
    
    return render(request, 'kiosco_app/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def editar_usuario(request, pk):
    # Solo administradores pueden editar usuarios
    if request.user.tipo_usuario != Usuario.ADMIN:
        messages.error(request, 'No tienes permisos para editar usuarios')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente')
            return redirect('lista_usuarios')
    else:
        form = RegistroUsuarioForm(instance=usuario)
    return render(request, 'kiosco_app/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def desactivar_usuario(request, pk):
    # Solo administradores pueden desactivar usuarios
    if request.user.tipo_usuario != Usuario.ADMIN:
        messages.error(request, 'No tienes permisos para desactivar usuarios')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    # Evitar que un administrador se desactive a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario')
        return redirect('lista_usuarios')
    
    usuario.is_active = False
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} desactivado correctamente')
    return redirect('lista_usuarios')

@login_required
def activar_usuario(request, pk):
    # Solo administradores pueden activar usuarios
    if request.user.tipo_usuario != Usuario.ADMIN:
        messages.error(request, 'No tienes permisos para activar usuarios')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.is_active = True
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} activado correctamente')
    return redirect('lista_usuarios')

@login_required
def confirmar_eliminar_usuario(request, pk):
    # Solo administradores pueden eliminar usuarios
    if request.user.tipo_usuario != Usuario.ADMIN:
        messages.error(request, 'No tienes permisos para eliminar usuarios')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    # Evitar que un administrador se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario')
        return redirect('lista_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado permanentemente')
        return redirect('lista_usuarios')
    
    return render(request, 'kiosco_app/confirmar_eliminar_usuario.html', {'usuario': usuario})

# Dashboard principal
@login_required
def dashboard(request):
    # Estadísticas básicas para el dashboard
    total_productos = Producto.objects.count()
    productos_sin_stock = Producto.objects.filter(stock=0).count()
    ventas_hoy = Venta.objects.filter(fecha__date=timezone.now().date()).count()
    ingresos_hoy = Venta.objects.filter(fecha__date=timezone.now().date()).aggregate(total=Sum('total'))['total'] or 0
    
    # Verificar si hay una caja abierta para el usuario actual
    caja_abierta = Caja.objects.filter(
        usuario=request.user,
        tipo_operacion=Caja.APERTURA,
        fecha_hora__date=timezone.now().date()
    ).exists()
    
    context = {
        'total_productos': total_productos,
        'productos_sin_stock': productos_sin_stock,
        'ventas_hoy': ventas_hoy,
        'ingresos_hoy': ingresos_hoy,
        'caja_abierta': caja_abierta,
    }
    return render(request, 'kiosco_app/dashboard.html', context)

# Vistas de productos
@login_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'kiosco_app/lista_productos.html', {'productos': productos})

@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    historial = producto.historial_precios.all().order_by('-fecha_cambio')
    return render(request, 'kiosco_app/detalle_producto.html', {
        'producto': producto,
        'historial': historial
    })

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto {producto.nombre} creado correctamente')
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'kiosco_app/form_producto.html', {'form': form, 'accion': 'Crear'})

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    precio_anterior = producto.precio
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto = form.save()
            
            # Si el precio cambió, registrar en el historial
            if precio_anterior != producto.precio:
                HistorialPrecio.objects.create(
                    producto=producto,
                    precio_anterior=precio_anterior,
                    precio_nuevo=producto.precio,
                    usuario=request.user
                )
                messages.info(request, f'Se registró el cambio de precio de {precio_anterior} a {producto.precio}')
            
            messages.success(request, f'Producto {producto.nombre} actualizado correctamente')
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'kiosco_app/form_producto.html', {
        'form': form, 
        'producto': producto,
        'accion': 'Editar'
    })

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto {nombre} eliminado correctamente')
        return redirect('lista_productos')
    
    return render(request, 'kiosco_app/confirmar_eliminar.html', {
        'objeto': producto,
        'tipo': 'producto'
    })

# Vistas de ventas
@login_required
def nueva_venta(request):
    # Verificar si hay una caja abierta
    caja_abierta = Caja.objects.filter(
        usuario=request.user,
        tipo_operacion=Caja.APERTURA,
        fecha_hora__date=timezone.now().date()
    ).exists()
    
    if not caja_abierta:
        messages.error(request, 'Debes abrir la caja antes de realizar ventas')
        return redirect('apertura_caja')
    
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        if venta_form.is_valid():
            venta = venta_form.save(commit=False)
            venta.usuario = request.user
            venta.total = 0  # Se calculará después
            venta.save()
            return redirect('agregar_detalle_venta', venta.id)
    else:
        venta_form = VentaForm()
    
    return render(request, 'kiosco_app/nueva_venta.html', {'form': venta_form})

@login_required
def agregar_detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    
    if request.method == 'POST':
        form = DetalleVentaForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.venta = venta
            
            # Verificar stock
            if detalle.cantidad > detalle.producto.stock:
                messages.error(request, f'No hay suficiente stock de {detalle.producto.nombre}')
                return redirect('agregar_detalle_venta', venta.id)
            
            # Calcular subtotal
            detalle.precio_unitario = detalle.producto.precio
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario
            detalle.save()
            
            # Actualizar stock
            detalle.producto.stock -= detalle.cantidad
            detalle.producto.save()
            
            # Actualizar total de la venta
            venta.total = DetalleVenta.objects.filter(venta=venta).aggregate(total=Sum('subtotal'))['total'] or 0
            venta.save()
            
            messages.success(request, f'Producto {detalle.producto.nombre} agregado a la venta')
            
            # Preguntar si desea agregar más productos
            if 'agregar_otro' in request.POST:
                return redirect('agregar_detalle_venta', venta.id)
            else:
                return redirect('finalizar_venta', venta.id)
    else:
        form = DetalleVentaForm()
    
    detalles = DetalleVenta.objects.filter(venta=venta)
    total = sum(detalle.subtotal for detalle in detalles)
    
    return render(request, 'kiosco_app/agregar_detalle_venta.html', {
        'form': form,
        'venta': venta,
        'detalles': detalles,
        'total': total
    })

@login_required
def finalizar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    
    if not venta.detalles.exists():
        messages.error(request, 'La venta no tiene productos')
        return redirect('agregar_detalle_venta', venta.id)
    
    if request.method == 'POST':
        # Actualizar caja
        try:
            caja = Caja.objects.get(
                usuario=request.user,
                tipo_operacion=Caja.APERTURA,
                fecha_hora__date=timezone.now().date()
            )
            caja.total_ventas += venta.total
            caja.save()
        except Caja.DoesNotExist:
            messages.error(request, 'No hay una caja abierta')
            return redirect('dashboard')
        
        messages.success(request, f'Venta #{venta.id} finalizada correctamente')
        return redirect('dashboard')
    
    return render(request, 'kiosco_app/finalizar_venta.html', {'venta': venta})

@login_required
def lista_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'kiosco_app/lista_ventas.html', {'ventas': ventas})

@login_required
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    return render(request, 'kiosco_app/detalle_venta.html', {
        'venta': venta,
        'detalles': detalles
    })

# Vistas de caja
@login_required
def apertura_caja(request):
    # Verificar si ya hay una caja abierta para el usuario actual
    caja_abierta = Caja.objects.filter(
        usuario=request.user,
        tipo_operacion=Caja.APERTURA,
        fecha_hora__date=timezone.now().date()
    ).exists()
    
    if caja_abierta:
        messages.error(request, 'Ya tienes una caja abierta')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario = request.user
            caja.tipo_operacion = Caja.APERTURA
            caja.save()
            messages.success(request, 'Caja abierta correctamente')
            return redirect('dashboard')
    else:
        form = AperturaCajaForm()
    
    return render(request, 'kiosco_app/apertura_caja.html', {'form': form})

@login_required
def cierre_caja(request):
    try:
        caja = Caja.objects.get(
            usuario=request.user,
            tipo_operacion=Caja.APERTURA,
            fecha_hora__date=timezone.now().date()
        )
    except Caja.DoesNotExist:
        messages.error(request, 'No hay una caja abierta')
        return redirect('dashboard')
    
    # Calcular total de ventas del día para este usuario
    ventas_dia = Venta.objects.filter(
        usuario=request.user,
        fecha__date=timezone.now().date()
    )
    total_ventas = ventas_dia.aggregate(total=Sum('total'))['total'] or 0
    
    if request.method == 'POST':
        form = CierreCajaForm(request.POST)
        if form.is_valid():
            # Crear registro de cierre
            cierre = Caja(
                usuario=request.user,
                tipo_operacion=Caja.CIERRE,
                monto_inicial=caja.monto_inicial,
                monto_final=form.cleaned_data['monto_final'],
                total_ventas=total_ventas,
                observaciones=form.cleaned_data['observaciones']
            )
            cierre.save()
            
            messages.success(request, 'Caja cerrada correctamente')
            return redirect('dashboard')
    else:
        # Pre-llenar el monto final con la suma del monto inicial más las ventas
        monto_final_sugerido = caja.monto_inicial + total_ventas
        form = CierreCajaForm(initial={'monto_final': monto_final_sugerido})
    
    return render(request, 'kiosco_app/cierre_caja.html', {
        'form': form,
        'caja_actual': caja,
        'total_ventas': total_ventas,
        'monto_final_esperado': caja.monto_inicial + total_ventas
    })

@login_required
def historial_caja(request):
    # Solo administradores pueden ver el historial completo
    if request.user.tipo_usuario == Usuario.ADMIN:
        registros = Caja.objects.all().order_by('-fecha_hora')
    else:
        # Empleados solo ven su historial
        registros = Caja.objects.filter(usuario=request.user).order_by('-fecha_hora')
    
    # Verificar si hay una caja abierta para el usuario actual
    # Buscamos la última apertura de caja del usuario que no tenga un cierre posterior
    ultima_apertura = Caja.objects.filter(
        usuario=request.user,
        tipo_operacion=Caja.APERTURA
    ).order_by('-fecha_hora').first()
    
    caja_abierta = False
    if ultima_apertura:
        # Verificar si hay un cierre posterior a la última apertura
        cierre_posterior = Caja.objects.filter(
            usuario=request.user,
            tipo_operacion=Caja.CIERRE,
            fecha_hora__gt=ultima_apertura.fecha_hora
        ).exists()
        
        caja_abierta = not cierre_posterior
    
    return render(request, 'kiosco_app/historial_caja.html', {
        'registros': registros,
        'caja_abierta': caja_abierta
    })
