import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from store.models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review


class Command(BaseCommand):
    help = 'Genera datos de prueba para el e-commerce KR Cases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de generar nuevos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Eliminando datos existentes...")
            Review.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Coupon.objects.all().delete()
            ProductVariant.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("✅ Datos eliminados."))

        self.stdout.write("Generando datos de prueba...")

        # --- Usuarios ---
        users = []
        user_data = [
            ('maria', 'maria@test.com', 'María', 'García'),
            ('carlos', 'carlos@test.com', 'Carlos', 'López'),
            ('ana', 'ana@test.com', 'Ana', 'Martínez'),
            ('juan', 'juan@test.com', 'Juan', 'Rodríguez'),
            ('laura', 'laura@test.com', 'Laura', 'Fernández'),
        ]
        for username, email, first, last in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)

        self.stdout.write(f"  → {len(users)} usuarios creados/encontrados")

        # --- Categorías ---
        categories_data = [
            ('Fundas iPhone', 'fundas-iphone'),
            ('Fundas Samsung', 'fundas-samsung'),
            ('Fundas Xiaomi', 'fundas-xiaomi'),
            ('Accesorios', 'accesorios'),
            ('Protectores de Pantalla', 'protectores-pantalla'),
        ]
        categories = []
        for name, slug in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, slug=slug)
            categories.append(cat)

        self.stdout.write(f"  → {len(categories)} categorías creadas")

        # --- Productos con Variantes ---
        products_data = [
            {
                'name': 'Funda Silicona Premium',
                'slug': 'funda-silicona-premium',
                'description': 'Funda de silicona de alta calidad con interior de microfibra. Protección completa contra caídas y arañazos.',
                'base_price': Decimal('45000'),
                'category': categories[0],
                'variants': [
                    ('iPhone 15', 'Negro', 'Silicona', 'SIL-IP15-NEG', 25),
                    ('iPhone 15', 'Azul Marino', 'Silicona', 'SIL-IP15-AZU', 15),
                    ('iPhone 15 Pro', 'Negro', 'Silicona', 'SIL-IP15P-NEG', 30),
                    ('iPhone 15 Pro', 'Rojo', 'Silicona', 'SIL-IP15P-ROJ', 10),
                    ('iPhone 15 Pro Max', 'Negro', 'Silicona', 'SIL-IP15PM-NEG', 20),
                ]
            },
            {
                'name': 'Funda Cuero Ejecutiva',
                'slug': 'funda-cuero-ejecutiva',
                'description': 'Funda de cuero genuino con acabado elegante. Ideal para uso profesional.',
                'base_price': Decimal('85000'),
                'category': categories[0],
                'variants': [
                    ('iPhone 15 Pro', 'Marrón', 'Cuero', 'CUE-IP15P-MAR', 12),
                    ('iPhone 15 Pro', 'Negro', 'Cuero', 'CUE-IP15P-NEG', 8),
                    ('iPhone 15 Pro Max', 'Marrón', 'Cuero', 'CUE-IP15PM-MAR', 6),
                ]
            },
            {
                'name': 'Funda Transparente Ultra Slim',
                'slug': 'funda-transparente-ultra-slim',
                'description': 'Funda transparente ultra delgada que muestra el diseño original del teléfono. Anti-amarillamiento.',
                'base_price': Decimal('25000'),
                'category': categories[0],
                'variants': [
                    ('iPhone 14', 'Transparente', 'TPU', 'TPU-IP14-TRA', 40),
                    ('iPhone 15', 'Transparente', 'TPU', 'TPU-IP15-TRA', 50),
                    ('iPhone 15 Pro', 'Transparente', 'TPU', 'TPU-IP15P-TRA', 45),
                ]
            },
            {
                'name': 'Funda Galaxy Armor',
                'slug': 'funda-galaxy-armor',
                'description': 'Funda resistente de doble capa para Samsung Galaxy. Protección militar contra caídas.',
                'base_price': Decimal('55000'),
                'category': categories[1],
                'variants': [
                    ('Galaxy S24', 'Negro', 'Policarbonato', 'ARM-GS24-NEG', 18),
                    ('Galaxy S24 Ultra', 'Negro', 'Policarbonato', 'ARM-GS24U-NEG', 22),
                    ('Galaxy S24 Ultra', 'Azul', 'Policarbonato', 'ARM-GS24U-AZU', 10),
                ]
            },
            {
                'name': 'Funda Samsung Wallet',
                'slug': 'funda-samsung-wallet',
                'description': 'Funda tipo billetera con espacio para tarjetas y cierre magnético.',
                'base_price': Decimal('65000'),
                'category': categories[1],
                'variants': [
                    ('Galaxy S24', 'Negro', 'Cuero Sintético', 'WAL-GS24-NEG', 15),
                    ('Galaxy S24 Ultra', 'Marrón', 'Cuero Sintético', 'WAL-GS24U-MAR', 10),
                ]
            },
            {
                'name': 'Funda Xiaomi Anti-Shock',
                'slug': 'funda-xiaomi-anti-shock',
                'description': 'Funda con esquinas reforzadas y tecnología de absorción de impactos.',
                'base_price': Decimal('35000'),
                'category': categories[2],
                'variants': [
                    ('Redmi Note 13', 'Negro', 'TPU Reforzado', 'ASH-RN13-NEG', 30),
                    ('Redmi Note 13 Pro', 'Negro', 'TPU Reforzado', 'ASH-RN13P-NEG', 25),
                    ('Poco X6', 'Transparente', 'TPU Reforzado', 'ASH-PX6-TRA', 20),
                ]
            },
            {
                'name': 'Protector Vidrio Templado',
                'slug': 'protector-vidrio-templado',
                'description': 'Vidrio templado 9H con bordes curvados 2.5D. Instalación sin burbujas.',
                'base_price': Decimal('15000'),
                'category': categories[4],
                'variants': [
                    ('iPhone 15', 'Transparente', 'Vidrio 9H', 'VID-IP15-TRA', 100),
                    ('iPhone 15 Pro', 'Transparente', 'Vidrio 9H', 'VID-IP15P-TRA', 80),
                    ('Galaxy S24', 'Transparente', 'Vidrio 9H', 'VID-GS24-TRA', 60),
                    ('Galaxy S24 Ultra', 'Transparente', 'Vidrio 9H', 'VID-GS24U-TRA', 50),
                ]
            },
            {
                'name': 'Cable USB-C Trenzado',
                'slug': 'cable-usb-c-trenzado',
                'description': 'Cable USB-C de nylon trenzado, 1.5m, carga rápida 65W. Compatible con todos los dispositivos USB-C.',
                'base_price': Decimal('20000'),
                'category': categories[3],
                'variants': [
                    ('1.5m', 'Negro', 'Nylon', 'CAB-15-NEG', 50),
                    ('1.5m', 'Blanco', 'Nylon', 'CAB-15-BLA', 35),
                    ('2m', 'Negro', 'Nylon', 'CAB-20-NEG', 40),
                ]
            },
        ]

        products = []
        total_variants = 0
        for pdata in products_data:
            variants_data = pdata.pop('variants')
            product, _ = Product.objects.get_or_create(
                slug=pdata['slug'],
                defaults=pdata
            )
            products.append(product)

            for model_name, color, material, sku, stock in variants_data:
                ProductVariant.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'product': product,
                        'model_name': model_name,
                        'color': color,
                        'material': material,
                        'stock': stock,
                    }
                )
                total_variants += 1

        self.stdout.write(f"  → {len(products)} productos, {total_variants} variantes creados")

        # --- Cupones ---
        now = timezone.now()
        coupons_data = [
            ('BIENVENIDO10', 'percentage', Decimal('10'), now - timedelta(days=30), now + timedelta(days=60)),
            ('VERANO20', 'percentage', Decimal('20'), now - timedelta(days=5), now + timedelta(days=25)),
            ('DESCUENTO5K', 'fixed', Decimal('5000'), now - timedelta(days=10), now + timedelta(days=20)),
        ]
        for code, dtype, value, vfrom, vto in coupons_data:
            Coupon.objects.get_or_create(
                code=code,
                defaults={
                    'discount_type': dtype,
                    'discount_value': value,
                    'valid_from': vfrom,
                    'valid_to': vto,
                    'active': True,
                }
            )

        self.stdout.write(f"  → {len(coupons_data)} cupones creados")

        # --- Órdenes de ejemplo ---
        all_variants = list(ProductVariant.objects.all())
        orders_created = 0

        for i in range(15):
            user = random.choice(users)
            days_ago = random.randint(0, 29)
            order_date = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            order_status = random.choices(
                ['PAID', 'PENDING', 'SHIPPED', 'CANCELLED'],
                weights=[50, 20, 20, 10]
            )[0]

            order = Order.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=f'09{random.randint(10000000, 99999999)}',
                address=f'Calle {random.randint(1, 100)}, Asunción',
                status=order_status,
                created_at=order_date,
            )
            # Override auto_now_add
            Order.objects.filter(pk=order.pk).update(created_at=order_date)

            total = Decimal('0')
            num_items = random.randint(1, 3)
            selected_variants = random.sample(all_variants, min(num_items, len(all_variants)))

            for variant in selected_variants:
                qty = random.randint(1, 3)
                price = variant.price
                OrderItem.objects.create(
                    order=order,
                    product_variant=variant,
                    quantity=qty,
                    price_at_purchase=price
                )
                total += price * qty

            order.total_amount = total
            order.save(update_fields=['total_amount'])
            orders_created += 1

        self.stdout.write(f"  → {orders_created} órdenes creadas")

        # --- Reseñas ---
        reviews_created = 0
        for product in products:
            num_reviews = random.randint(1, 4)
            reviewers = random.sample(users, min(num_reviews, len(users)))

            for user in reviewers:
                comments = [
                    "Excelente calidad, justo lo que buscaba.",
                    "Muy buena funda, protege bien el teléfono.",
                    "Calidad precio inmejorable. Recomendado.",
                    "Se ve premium. Mi teléfono queda protegido y elegante.",
                    "Buena pero podría ser un poco más gruesa.",
                    "Perfecta, envío rápido y bien empaquetado.",
                    "Regular, el color no era exactamente como en la foto.",
                    "Muy contento con la compra. Ya es mi segunda funda de esta marca.",
                ]
                Review.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        'rating': random.randint(3, 5),
                        'comment': random.choice(comments),
                    }
                )
                reviews_created += 1

        self.stdout.write(f"  → {reviews_created} reseñas creadas")

        self.stdout.write(self.style.SUCCESS(
            "\n🎉 ¡Datos de prueba generados exitosamente!\n"
            "  Usuarios de prueba: maria, carlos, ana, juan, laura (password: testpass123)\n"
            "  Cupones: BIENVENIDO10, VERANO20, DESCUENTO5K"
        ))
