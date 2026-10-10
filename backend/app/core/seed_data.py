from __future__ import annotations

from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.models.category import Category
from app.models.supplier import Supplier
from app.models.product import Product, ProductUnit
from app.models.customer import Customer, CustomerType
from app.models.inventory import InventoryMovement, MovementType


async def seed_initial_data(session: AsyncSession) -> None:
    """Inserta datos de demostración si la base de datos está vacía."""
    # Verificar si ya existen productos
    count_prod = (await session.execute(select(func.count(Product.id)))).scalar() or 0
    if count_prod > 0:
        return

    # 1. Categorías típicas de tienda de abarrotes
    categories_data = [
        {"name": "Lácteos y Huevos", "code": "LAC", "icon": "🥛", "color": "blue", "description": "Leche, quesos, mantequilla y huevos"},
        {"name": "Abarrotes y Granos", "code": "ABA", "icon": "🌾", "color": "amber", "description": "Arroz, azúcar, fideos, menestras y aceites"},
        {"name": "Bebidas y Gaseosas", "code": "BEB", "icon": "🥤", "color": "emerald", "description": "Gaseosas, aguas, jugos y cervezas"},
        {"name": "Aseo y Limpieza", "code": "ASE", "icon": "🧼", "color": "cyan", "description": "Detergentes, jabones, lejía y papel higiénico"},
        {"name": "Snacks y Golosinas", "code": "SNA", "icon": "🍫", "color": "purple", "description": "Galletas, chocolates, papitas y caramelos"},
        {"name": "Conservas y Enlatados", "code": "CON", "icon": "🥫", "color": "rose", "description": "Atún, duraznos, conservas de pescado y verduras"},
        {"name": "Panadería y Desayuno", "code": "PAN", "icon": "🥖", "color": "orange", "description": "Pan, avena, café y mermeladas"},
    ]

    cat_objs = {}
    for c_info in categories_data:
        cat = Category(
            name=c_info["name"],
            code=c_info["code"],
            icon=c_info["icon"],
            color=c_info["color"],
            description=c_info["description"],
            is_active=True
        )
        session.add(cat)
        await session.flush()
        cat_objs[c_info["code"]] = cat.id

    # 2. Proveedores
    suppliers_data = [
        {"company_name": "Distribuidora Alicorp S.A.A.", "ruc": "20100055237", "contact_name": "Carlos Mendoza", "phone": "987111222"},
        {"company_name": "Gloria Alimentos S.A.", "ruc": "20100190797", "contact_name": "Rosa Valdivia", "phone": "987333444"},
        {"company_name": "Arca Continental Lindley (Coca-Cola / Inca Kola)", "ruc": "20415504508", "contact_name": "Jorge Ramos", "phone": "987555666"},
    ]
    supp_ids = []
    for s_info in suppliers_data:
        supp = Supplier(
            company_name=s_info["company_name"],
            ruc=s_info["ruc"],
            contact_name=s_info["contact_name"],
            phone=s_info["phone"],
            is_active=True
        )
        session.add(supp)
        await session.flush()
        supp_ids.append(supp.id)

    # 3. Productos representativos de abarrotes con stock y alertas
    products_data = [
        # Lácteos
        {"name": "Leche Gloria Azul Evaporada 400g", "sku": "GLOR-001", "barcode": "7750151000101", "cat": "LAC", "unit": ProductUnit.UNIDAD, "cost": 3.40, "sale": 4.20, "stock": 48.0, "min": 10.0},
        {"name": "Huevos Pardos Frescos x Kilo", "sku": "HUEV-001", "barcode": "7750151001207", "cat": "LAC", "unit": ProductUnit.KILOGRAMO, "cost": 6.80, "sale": 8.50, "stock": 4.0, "min": 15.0}, # Alerta stock bajo
        {"name": "Mantequilla Gloria con Sal 200g", "sku": "GLOR-002", "barcode": "7750151000150", "cat": "LAC", "unit": ProductUnit.UNIDAD, "cost": 5.20, "sale": 6.80, "stock": 18.0, "min": 5.0},
        
        # Abarrotes y granos
        {"name": "Arroz Costeño Extra 1kg", "sku": "COST-001", "barcode": "7750151000200", "cat": "ABA", "unit": ProductUnit.KILOGRAMO, "cost": 4.10, "sale": 4.90, "stock": 85.0, "min": 20.0},
        {"name": "Aceite Primor Premium 1 Litro", "sku": "PRIM-001", "barcode": "7750151000309", "cat": "ABA", "unit": ProductUnit.LITRO, "cost": 8.50, "sale": 10.50, "stock": 32.0, "min": 10.0},
        {"name": "Azúcar Rubia Cartavio 1kg", "sku": "CART-001", "barcode": "7750151000408", "cat": "ABA", "unit": ProductUnit.KILOGRAMO, "cost": 3.60, "sale": 4.40, "stock": 60.0, "min": 15.0},
        {"name": "Fideos Don Vittorio Spaghetti 450g", "sku": "DVIT-001", "barcode": "7750151000507", "cat": "ABA", "unit": ProductUnit.UNIDAD, "cost": 2.80, "sale": 3.50, "stock": 45.0, "min": 12.0},
        
        # Bebidas
        {"name": "Inca Kola 1.5L No Retornable", "sku": "INCA-001", "barcode": "7750151000606", "cat": "BEB", "unit": ProductUnit.UNIDAD, "cost": 5.50, "sale": 7.00, "stock": 36.0, "min": 12.0},
        {"name": "Coca Cola 1.5L No Retornable", "sku": "COCA-001", "barcode": "7750151000705", "cat": "BEB", "unit": ProductUnit.UNIDAD, "cost": 5.50, "sale": 7.00, "stock": 24.0, "min": 10.0},
        {"name": "Agua San Mateo sin Gas 600ml", "sku": "SMAT-001", "barcode": "7750151000750", "cat": "BEB", "unit": ProductUnit.UNIDAD, "cost": 1.50, "sale": 2.50, "stock": 30.0, "min": 8.0},

        # Aseo
        {"name": "Detergente Bolívar Floral 800g", "sku": "BOLI-001", "barcode": "7750151000903", "cat": "ASE", "unit": ProductUnit.UNIDAD, "cost": 6.80, "sale": 8.50, "stock": 25.0, "min": 8.0},
        {"name": "Jabón Bolívar Ropa x 3 Unidades", "sku": "BOLJ-001", "barcode": "7750151001009", "cat": "ASE", "unit": ProductUnit.PAQUETE, "cost": 3.80, "sale": 5.00, "stock": 2.0, "min": 10.0}, # Alerta stock bajo
        {"name": "Papel Higiénico Suave Paquete 4u", "sku": "SUAV-001", "barcode": "7750151001108", "cat": "ASE", "unit": ProductUnit.PAQUETE, "cost": 4.20, "sale": 5.50, "stock": 40.0, "min": 12.0},

        # Snacks y Enlatados
        {"name": "Galletas Margarita Clásica 6pk", "sku": "MARG-001", "barcode": "7750151000804", "cat": "SNA", "unit": ProductUnit.PAQUETE, "cost": 2.20, "sale": 3.00, "stock": 35.0, "min": 10.0},
        {"name": "Atún Florida Filete en Aceite 170g", "sku": "FLOR-001", "barcode": "7750151001306", "cat": "CON", "unit": ProductUnit.LATA, "cost": 4.80, "sale": 6.20, "stock": 28.0, "min": 8.0},
    ]

    for p in products_data:
        cat_id = cat_objs.get(p["cat"])
        prod = Product(
            category_id=cat_id,
            supplier_id=supp_ids[0] if supp_ids else None,
            name=p["name"],
            sku=p["sku"],
            barcode=p["barcode"],
            unit=p["unit"],
            cost_price=p["cost"],
            sale_price=p["sale"],
            current_stock=p["stock"],
            min_stock=p["min"],
            is_active=True
        )
        session.add(prod)
        await session.flush()

        # Movimiento inicial en kárdex
        mov = InventoryMovement(
            product_id=prod.id,
            movement_type=MovementType.ENTRADA,
            quantity=p["stock"],
            previous_stock=0.0,
            new_stock=p["stock"],
            reason="Carga de inventario inicial",
            reference_document=f"INIT-{p['sku']}"
        )
        session.add(mov)

    # 4. Clientes habituales para el libro de fiados
    customers_data = [
        {"name": "Don Juan Pérez (Vecino Cuadra 2)", "dni": "10234567", "phone": "987111222", "limit": 150.0, "debt": 32.50, "type": CustomerType.FRECUENTE},
        {"name": "Doña María Rodríguez (Bodeguera)", "dni": "45678912", "phone": "987444555", "limit": 250.0, "debt": 0.0, "type": CustomerType.MAYORISTA},
        {"name": "Vecina Rosa Castillo", "dni": "78912345", "phone": "987777888", "limit": 100.0, "debt": 48.00, "type": CustomerType.REGULAR},
    ]

    for c in customers_data:
        cust = Customer(
            name=c["name"],
            document_type="DNI",
            document_number=c["dni"],
            phone=c["phone"],
            credit_limit=c["limit"],
            current_debt=c["debt"],
            customer_type=c["type"]
        )
        session.add(cust)

    await session.commit()
