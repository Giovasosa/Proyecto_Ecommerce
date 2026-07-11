import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kr_cases_project.settings')
django.setup()

from store.models import Category, Product, ProductVariant

data = {
    'Silicone Premium': [
        ('Silicone Pro Max', 'Funda de silicona líquida premium con interior de microfibra.', 120000, 'products/silicone_pro_max.png'),
        ('Silicone Lite', 'Silicona suave, flexible y ultra ligera.', 110000, 'products/silicone_lite.png'),
        ('Silicone Ultra Grip', 'Silicona texturizada para un agarre insuperable.', 130000, 'products/silicone_ultra_grip.png'),
    ],
    'Transparent Series': [
        ('Clear Crystal Case', 'Funda totalmente transparente con tecnología antiamarilleo.', 140000, 'products/clear_crystal.png'),
        ('Clear Edge Pro', 'Transparente con bordes reforzados para mayor protección.', 150000, 'products/clear_edge_pro.png'),
        ('Clear MagSafe', 'Transparente 100% compatible con accesorios MagSafe.', 160000, 'products/clear_magsafe.png'),
    ],
    'Matte Series': [
        ('Matte Black Classic', 'Negro mate elegante, resistente a rayones y sin huellas.', 135000, 'products/matte_black_classic.png'),
        ('Matte Frost', 'Acabado escarchado mate que resalta el color de tu teléfono.', 145000, 'products/matte_frost.png'),
        ('Matte Shield', 'Protección mate reforzada con policarbonato rígido.', 155000, 'products/matte_shield.png'),
    ],
    'Leather Premium': [
        ('Vintage Leather Cover', 'Cuero vintage premium seleccionado a mano.', 180000, 'products/vintage_leather.png'),
        ('Classic Leather Wallet', 'Funda de cuero premium tipo billetera con tarjetero.', 200000, 'products/leather_case.png'),
        ('Modern Leather Slim', 'Cuero moderno súper delgado y sofisticado.', 190000, 'products/leather_case.png'),
    ],
    'Armor Series': [
        ('Tactical Armor Case', 'Funda armadura táctica resistente a caídas extremas.', 165000, 'products/armor_case.png'),
        ('Heavy Duty Shield', 'Protección multicapa para uso en exteriores.', 175000, 'products/armor_case.png'),
        ('Armor Pro Max', 'Armadura con bordes de aluminio aeroespacial.', 210000, 'products/armor_case.png'),
    ],
    'Carbon Series': [
        ('Carbon Fiber Pro', 'Fibra de carbono real, ligera y ultra resistente.', 220000, 'products/carbon_case.png'),
        ('Carbon Aero Shell', 'Diseño aerodinámico esculpido en fibra de carbono.', 230000, 'products/carbon_case.png'),
        ('Carbon Grip Edge', 'Fibra de carbono con laterales de goma antideslizante.', 215000, 'products/carbon_case.png'),
    ]
}

for cat_name, products in data.items():
    cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': cat_name.lower().replace(' ', '-')})
    for idx, (p_name, desc, price, img) in enumerate(products):
        slug = p_name.lower().replace(' ', '-')
        # Si ya existe, actualiza la imagen
        p, created = Product.objects.update_or_create(
            slug=slug,
            defaults={
                'name': p_name,
                'description': desc,
                'base_price': price,
                'image': img,
                'category': cat,
                'is_active': True
            }
        )
        if created:
            ProductVariant.objects.create(
                product=p,
                model_name='iPhone 15 Pro',
                color='Dark',
                material=cat_name,
                sku=f'SKU-{slug}-15P',
                stock=10,
                price_override=price
            )
            ProductVariant.objects.create(
                product=p,
                model_name='Samsung S24',
                color='Dark',
                material=cat_name,
                sku=f'SKU-{slug}-S24',
                stock=5,
                price_override=price
            )

print("Products added successfully!")
