window.addEventListener("load", function() {
    const loader = document.getElementById("loader-wrapper");
    // Añadir un pequeño retraso para que la rueda sea apreciable
    setTimeout(() => {
        loader.style.opacity = "0";
        setTimeout(() => {
            loader.style.display = "none";
        }, 500); // 500ms coincide con la transición CSS
    }, 300); // 300ms de visibilidad mínima
});
