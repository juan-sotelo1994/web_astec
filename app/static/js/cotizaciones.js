// cotizaciones.js
let productosData = [];
let serviciosData = [];

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('json-data-container');
    if (container) {
        const rawProductos = JSON.parse(container.dataset.productos || '[]');
        const rawServicios = JSON.parse(container.dataset.servicios || '[]');

        productosData = rawProductos.map(p => ({
            id: p.id_producto,
            nombre: p.nombre_producto,
            precio: parseFloat(p.precio_unitario_producto || 0)
        }));

        serviciosData = rawServicios.map(s => ({
            id: s.id_servicio,
            nombre: s.nombre,
            precio: 0
        }));
    }
});

function calculateTotal() {
    let gt = 0;
    const prices = document.querySelectorAll('.line-precio');
    const qtys = document.querySelectorAll('.line-qty');
    for (let i = 0; i < prices.length; i++) {
        const p = parseFloat(prices[i].value) || 0;
        const q = parseFloat(qtys[i].value) || 0;
        gt += (p * q);
    }
    document.getElementById('total').value = gt.toFixed(2);
}

function changeLineType(sel) {
    const row = sel.closest('.linea-row');
    const itemSel = row.querySelector('.line-item');
    const tipo = sel.value;
    itemSel.innerHTML = '<option value="">Seleccione...</option>';
    if (tipo === 'producto') {
        productosData.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id; opt.textContent = p.nombre; opt.dataset.precio = p.precio;
            itemSel.appendChild(opt);
        });
    } else {
        serviciosData.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id; opt.textContent = s.nombre; opt.dataset.precio = s.precio;
            itemSel.appendChild(opt);
        });
    }
    itemSel.value = "";
    row.querySelector('.line-precio').value = "";
    calculateTotal();
}

function changeLineItem(sel) {
    const row = sel.closest('.linea-row');
    const precioInput = row.querySelector('.line-precio');
    if (sel.selectedIndex > 0) {
        precioInput.value = sel.options[sel.selectedIndex].dataset.precio;
    } else {
        precioInput.value = "";
    }
    calculateTotal();
}

function addLinea() {
    const container = document.getElementById('lineas-container');
    const row = document.createElement('div');
    row.className = 'linea-row';
    row.style.display = 'grid';
    row.style.gridTemplateColumns = '100px 2fr 100px 150px 40px';
    row.style.gap = '10px';
    row.style.alignItems = 'center';

    row.innerHTML = `
        <select name="item_tipo[]" class="line-tipo" onchange="changeLineType(this)" required style="padding: 0.5rem; font-size: 13px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="producto" selected>Producto</option>
            <option value="servicio">Servicio</option>
        </select>
        <select name="item_id[]" class="line-item" onchange="changeLineItem(this)" required style="padding: 0.5rem; font-size: 13px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="">Seleccione...</option>
        </select>
        <input type="number" name="item_cantidad[]" class="line-qty" value="1" min="1" step="1" oninput="calculateTotal()" required style="padding: 0.5rem; font-size: 13px; border-radius: 4px; border: 1px solid #ccc;" placeholder="Cant.">
        <input type="number" name="item_precio[]" class="line-precio" step="0.01" oninput="calculateTotal()" required style="padding: 0.5rem; font-size: 13px; border-radius: 4px; border: 1px solid #ccc;" placeholder="Precio Unit.">
        <button type="button" onclick="this.closest('.linea-row').remove(); calculateTotal();" style="background: transparent; border: none; color: #dc3545; cursor: pointer; font-size: 16px;"><i class="fa-solid fa-trash"></i></button>
    `;
    container.appendChild(row);
    changeLineType(row.querySelector('.line-tipo')); // init products
}

function toggleForm() {
    var formContainer = document.getElementById("form-container");
    var btnToggle = document.getElementById("btnToggleForm");

    if (formContainer.style.display === "none") {
        formContainer.style.display = "block";
        btnToggle.innerHTML = '<i class="fa-solid fa-minus"></i> Ocultar Formulario';
        btnToggle.style.backgroundColor = '#e74c3c';
        formContainer.scrollIntoView({ behavior: 'smooth' });
    } else {
        formContainer.style.display = "none";
        btnToggle.innerHTML = '<i class="fa-solid fa-plus"></i> Añadir Cotización';
        btnToggle.style.backgroundColor = '#005b9f';
        cancelEdit();
    }
}

function editCotizacion(btn) {
    var formContainer = document.getElementById("form-container");
    if (formContainer.style.display === "none") {
        toggleForm();
    } else {
        formContainer.scrollIntoView({ behavior: 'smooth' });
    }
    document.getElementById('id_edit').value = btn.dataset.id;
    document.getElementById('cliente_id').value = btn.dataset.cli;
    document.getElementById('vendedor_id').value = btn.dataset.ven;

    if(document.getElementById('fecha_emision')) {
        document.getElementById('fecha_emision').value = btn.dataset.emi || '';
    }
    if(document.getElementById('fecha_vencimiento')) {
        document.getElementById('fecha_vencimiento').value = btn.dataset.venc || '';
    }
    if(document.getElementById('observaciones')) {
        document.getElementById('observaciones').value = btn.dataset.obs || '';
    }

    document.getElementById('estado').value = btn.dataset.est;
    document.getElementById('total').value = btn.dataset.tot;

    document.getElementById('btnSubmitText').textContent = 'Actualizar Cotización';
    document.getElementById('btnCancelEdit').style.display = 'block';
}

function cancelEdit() {
    document.getElementById('id_edit').value = '';
    document.getElementById('form-cotizacion').reset();
    document.getElementById('lineas-container').innerHTML = ''; // Limpiar líneas
    document.getElementById('btnSubmitText').textContent = 'Guardar Cotización';
    document.getElementById('btnCancelEdit').style.display = 'none';
    calculateTotal();
}
