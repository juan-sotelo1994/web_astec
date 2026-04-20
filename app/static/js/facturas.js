// facturas.js

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
        btnToggle.innerHTML = '<i class="fa-solid fa-plus"></i> Expedir Nueva Factura';
        btnToggle.style.backgroundColor = '#005b9f';
        cancelEdit();
    }
}

function editFactura(buttonElement) {
    var dataset = buttonElement.dataset;

    document.getElementById('id_edit').value = dataset.id;
    document.getElementById('numero_factura').value = dataset.num;
    document.getElementById('venta_id').value = dataset.venta;
    document.getElementById('estado_factura').value = dataset.estado;

    document.getElementById('formTitle').textContent = 'Edición de Documento';
    document.getElementById('btnSubmitText').textContent = 'Actualizar Factura';
    document.getElementById('btnCancelEdit').style.display = 'block';

    var formContainer = document.getElementById("form-container");
    if (formContainer.style.display === "none") {
        toggleForm();
    } else {
        formContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

function cancelEdit() {
    document.getElementById('id_edit').value = '';
    document.getElementById('form-factura').reset();
    document.getElementById('formTitle').textContent = 'Generar Documento Contable';
    document.getElementById('btnSubmitText').textContent = 'Registrar Factura Legal';
    document.getElementById('btnCancelEdit').style.display = 'none';
}
