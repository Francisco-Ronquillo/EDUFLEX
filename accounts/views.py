from NIÑO.models import Niño
from PADRE.models import  Padre
from PROFESOR.models import Profesor
from accounts.forms.signupkid import NiñoForm
from accounts.forms.signupDad import PadreForm
from django.shortcuts import render, redirect
from django.views.generic import TemplateView,CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from accounts.models import *
from accounts.forms.recover_password import *
from django.conf import settings
from django.core.mail import send_mail
from EDUFLEX.utils import *

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

class LoginView(TemplateView):
    template_name = 'login.html'
    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)

    def post(self, request):
        if 'usuario_padre' in request.POST:
            usuario = request.POST['usuario_padre']
            clave =cifrar_contraseña(request.POST['clave_padre'])

            try:
                padre = Padre.objects.get(usuario=usuario, contraseña=clave)
                request.session['padre_id'] = padre.id
                return redirect('padre:dashboardDad')
            except Padre.DoesNotExist:
                messages.error(request, "Credenciales incorrectas para padre.")
                return render(request, self.template_name)
        elif 'usuario_nino' in request.POST:
            usuario = request.POST['usuario_nino']
            clave = cifrar_contraseña(request.POST['clave_nino'])

            try:
                nino = Niño.objects.get(usuario=usuario, contraseña=clave)
                request.session['nino_id'] = nino.id
                return redirect('niño:dashboardKid')
            except Niño.DoesNotExist:
                messages.error(request, "Credenciales incorrectas para niño.")
                return render(request, self.template_name)
        elif 'usuario_profesor' in request.POST:
            usuario = request.POST['usuario_profesor']
            clave = cifrar_contraseña(request.POST['clave_profesor'])

            try:
                profesor = Profesor.objects.get(usuario=usuario, contraseña=clave)
                request.session['profesor_id'] = profesor.id
                return redirect('profesor:dashboardTeacher')
            except Profesor.DoesNotExist:
                messages.error(request, "Credenciales incorrectas para niño.")
                return render(request, self.template_name)

        messages.error(request, "Formulario no válido.")
        return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect('accounts:login')

class RolView(TemplateView):
    template_name = 'rol.html'
    def get_context_data(self, **kwargs):
        context = super(RolView, self).get_context_data(**kwargs)

class SignupKidView(CreateView):
    model = Niño
    form_class = NiñoForm
    template_name = 'signupKid.html'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super(SignupKidView, self).get_context_data(**kwargs)
        return context
    def form_valid(self, form):
        contraseña_plana = form.cleaned_data['contraseña']
        contraseña_cifrada = hashlib.sha256(contraseña_plana.encode()).hexdigest()
        form.instance.contraseña = contraseña_cifrada
        form.instance.codigo = generar_codigo_unico()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al crear la cuenta. Revisa los campos.")
        return self.render_to_response(self.get_context_data(form=form))

class SignupDadView(CreateView):
    model = Padre
    form_class = PadreForm
    template_name = 'signupDad.html'
    success_url = reverse_lazy('accounts:login')
    def get_context_data(self, **kwargs):
        context = super(SignupDadView, self).get_context_data(**kwargs)
        return  context

    def form_valid(self, form):

        contraseña_plana = form.cleaned_data['contraseña']
        contraseña_cifrada = hashlib.sha256(contraseña_plana.encode()).hexdigest()

        form.instance.contraseña = contraseña_cifrada

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al crear la cuenta. Revisa los campos.")
        return self.render_to_response(self.get_context_data(form=form))




class EnviarCodigoView(View):
    template_name = 'recover_password.html'

    def get(self, request, rol):
        request.session['tipo_usuario'] = rol
        return render(request, self.template_name, {'form': SolicitarCodigoForm()})

    def post(self, request, rol):
        form = SolicitarCodigoForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            tipo_usuario = rol.lower()
            usuario_obj = None

            if tipo_usuario == 'padre':
                print('→ Solicitud de padre')
                if Padre.objects.filter(email=email).exists():
                    usuario_obj = Padre.objects.get(email=email)
                else:
                    messages.error(request, "No hay un padre con ese correo.")
                    return render(request, self.template_name, {'form': form})

            elif tipo_usuario == 'niño':
                if Niño.objects.filter(email=email).exists():
                    usuario_obj = Niño.objects.get(email=email)
                else:
                    messages.error(request, "No hay un niño con ese correo.")
                    return render(request, self.template_name, {'form': form})
            else:
                messages.error(request, "Tipo de usuario inválido.")
                return render(request, self.template_name, {'form': form})


            request.session['recuperacion_email'] = email
            request.session['tipo_usuario'] = tipo_usuario


            codigo = str(random.randint(100000, 999999))
            CodigoRecuperacion.objects.create(email=email, codigo=codigo)

            # Enviar el correo con el remitente verificado
            try:
                send_mail(
                    'Código de recuperación - Eduflex',
                    f'Tu código es: {codigo}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

            except Exception as e:

                messages.error(request, f"Error al enviar el correo: {e}")
                return render(request, self.template_name, {'form': form})

            messages.success(request, "Código enviado a tu correo.")
            return redirect('accounts:verificar_codigo')

        return render(request, self.template_name, {'form': form})


class VerificarCodigoView(View):
    template_name = 'validate_code.html'

    def get(self, request):
        return render(request, self.template_name, {'form': VerificarCodigoForm()})

    def post(self, request):
        form = VerificarCodigoForm(request.POST)
        email = request.session.get('recuperacion_email')

        if form.is_valid() and email:
            codigo = form.cleaned_data['codigo']
            codigos = CodigoRecuperacion.objects.filter(email=email, codigo=codigo).order_by('-creado_en')

            if codigos and not codigos[0].expirado():
                request.session['codigo_validado'] = True
                return redirect('accounts:cambiar_contraseña')
            else:
                messages.error(request, "Código inválido o expirado.")

        return render(request, self.template_name, {'form': form})



class CambiarContraseñaConCodigoView(View):
    template_name = 'new_password.html'

    def get(self, request):
        if not request.session.get('codigo_validado'):
            return redirect('accounts:verificar_codigo')
        return render(request, self.template_name, {'form': NuevaContraseñaForm()})

    def post(self, request):
        form = NuevaContraseñaForm(request.POST)
        email = request.session.get('recuperacion_email')
        tipo = request.session.get('tipo_usuario')

        if form.is_valid() and email and tipo:
            nueva = cifrar_contraseña(form.cleaned_data['nueva'])

            try:
                if tipo == 'padre':
                    usuario = Padre.objects.get(email=email)
                elif tipo == 'niño':
                    usuario = Niño.objects.get(email=email)
                else:
                    raise ValueError("Tipo de usuario inválido")

                usuario.contraseña = nueva
                usuario.save()
                messages.success(request, "Contraseña actualizada correctamente.")
                request.session.flush()
                return redirect('accounts:login')

            except (Padre.DoesNotExist, Niño.DoesNotExist):
                messages.error(request, "No se encontró el usuario.")

        return render(request, self.template_name, {'form': form})
