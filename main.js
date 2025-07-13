// main.js profesional para hoteles

// --- Función slugify simple para URLs ---
function slugify(text) {
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Reemplaza espacios por -
    .replace(/[áàäâ]/g, 'a')         // Normaliza acentos
    .replace(/[éèëê]/g, 'e')
    .replace(/[íìïî]/g, 'i')
    .replace(/[óòöô]/g, 'o')
    .replace(/[úùüû]/g, 'u')
    .replace(/ñ/g, 'n')
    .replace(/[^\w\-]+/g, '')      // Elimina todo lo que no sea palabra o -
    .replace(/\-\-+/g, '-')        // Reemplaza múltiples - por uno solo
    .replace(/^-+/, '')              // Quita - al inicio
    .replace(/-+$/, '');             // Quita - al final
}

// --- Funciones mínimas para evitar errores JS ---
function mostrarSpinner(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '<div class="col-12 text-center text-muted">Cargando hoteles...</div>';
    }
}
function mostrarError(containerId, mensaje) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="col-12 text-center text-danger">${mensaje}</div>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarRecomendaciones();
    cargarHoteles();
    AOS.init({ duration: 900, once: true });
});

// --- Cargar y renderizar recomendaciones ---
function cargarRecomendaciones() {
    fetch('/api/recomendaciones')
        .then(res => res.json())
        .then(hotels => {
            renderHotelCards(hotels, 'recomendaciones');
        })
        .catch(() => {
            document.getElementById('recomendaciones').innerHTML = '<div class="col-12 text-center text-muted">No hay recomendaciones aún.</div>';
        });
}

// --- Cargar y renderizar todos los hoteles ---
let _hoteles = [];
function cargarHoteles() {
    mostrarSpinner('hotels');
    fetch('/api/hotels')
        .then(res => res.json())
        .then(hotels => {
            if (!Array.isArray(hotels)) {
                mostrarError('hotels', 'Error al cargar hoteles. Intenta de nuevo.');
                console.error('Respuesta inesperada de /api/hotels:', hotels);
                return;
            }
            console.log('Hoteles recibidos:', hotels.length, hotels);
            _hoteles = hotels;
            renderFilters(hotels);
            renderHotelCards(hotels, 'hotels');
        })
        .catch(() => {
            mostrarError('hotels', 'No se pudieron cargar los hoteles. Intenta de nuevo.');
        });
}

// --- Renderizado de tarjetas de hotel ---
function renderHotelCards(hotels, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    if (!hotels || hotels.length === 0) {
        container.innerHTML = '<div class="col-12 text-center text-muted">No hay hoteles disponibles.</div>';
        return;
    }
    hotels.forEach((hotel, i) => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';
        col.setAttribute('data-aos', i % 2 === 0 ? 'fade-up' : 'fade-down');
        const slug = hotel.slug || slugify(hotel.name);
        col.innerHTML = `
            <div class="card h-100 shadow-lg border-0 hotel-card position-relative" style="cursor:pointer; overflow:hidden;" data-hotel-slug="${slug}">
                <img src="${hotel.image || '/static/img/hotel_default.jpg'}" class="card-img-top" alt="${hotel.name}" style="height:260px; object-fit:cover;">
                <div class="card-body bg-white p-4 d-flex flex-column justify-content-between">
                  <div>
                    ${renderStars(hotel.stars)}
                    <h5 class="card-title hotel-nombre mb-2">${hotel.name}</h5>
                    <div class="mb-2">${renderPrice(hotel.price, hotel.name, hotel.location, true)}</div>
                    <div class="mb-2"><i class="bi bi-geo-alt"></i> <span class="text-muted">${hotel.location || 'No disponible'}</span></div>
                  </div>
                </div>
            </div>
        `;
        col.querySelector('.card').addEventListener('click', function() {
          window.location.href = `/hotel/${slug}`;
        });
        container.appendChild(col);
    });
    AOS.refresh();
}

function renderStars(stars) {
    let starsHtml = '';
    let starsNum = 0;
    if (stars && stars !== 'No disponible' && stars !== 'Sin clasificar') {
        let match = String(stars).match(/(\d+)/);
        if (match) {
            starsNum = parseInt(match[1]);
        }
        starsHtml = `<div class='mb-2'>`;
        for (let j = 1; j <= 5; j++) {
            if (j <= starsNum) {
                starsHtml += `<span style='color:#ffd700; font-size:1.4em;'>&#9733;</span>`;
            } else {
                starsHtml += `<span style='color:#ffd700; opacity:0.18; font-size:1.4em;'>&#9733;</span>`;
            }
        }
        starsHtml += `</div>`;
    } else {
        starsHtml = `<span class='badge bg-info text-dark mb-2'>Sin clasificar</span>`;
    }
    return starsHtml;
}

function renderPrice(price, name, location, hideConsultar) {
    if ((!price || price === 'N/D' || price === 'Consultar') && !hideConsultar) {
        return `<span class='badge bg-secondary fs-5 px-3 py-2 mb-2'>Consultar</span><br><a href='https://www.google.com/search?q=${encodeURIComponent(name + ' ' + (location || ''))}+precio+hotel' target='_blank' class='btn btn-outline-primary btn-sm mt-2'>Buscar precio en Google</a>`;
    }
    if ((!price || price === 'N/D' || price === 'Consultar') && hideConsultar) {
        return '';
    }
    return `<span class='badge bg-success fs-5 px-3 py-2 mb-2'>${price}</span>`;
}

// --- Configuración de Fuse.js para búsqueda difusa ---
let fuse = null;
let fuseOptions = {
  keys: [
    'name', 'location', 'stars', 'rating', 'valoracion_promedio', 'amenities', 'description', 'type', 'price'
  ],
  threshold: 0.38, // Sensibilidad de coincidencia
  minMatchCharLength: 2,
  includeScore: true,
  ignoreLocation: true,
  useExtendedSearch: true
};

// --- Renderizado de sugerencias de autocompletado ---
function renderAutocompleteSuggestions(suggestions, searchTerm) {
  let acBox = document.getElementById('autocomplete-suggestions');
  if (!acBox) {
    acBox = document.createElement('div');
    acBox.id = 'autocomplete-suggestions';
    acBox.className = 'autocomplete-suggestions shadow-lg';
    document.getElementById('filters').appendChild(acBox);
  }
  acBox.innerHTML = '';
  if (!suggestions.length) {
    acBox.innerHTML = `<div class='autocomplete-nores text-center p-3'><span style='font-size:2em;'>😕</span><br><span class='text-muted'>No se encontraron resultados<br><small>¡Prueba con otra palabra!</small></span></div>`;
    acBox.style.display = 'block';
    return;
  }
  suggestions.slice(0, 7).forEach(s => {
    const h = s.item;
    const slug = h.slug || slugify(h.name);
    let highlight = (txt) => {
      if (!searchTerm) return txt;
      let re = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      return txt.replace(re, '<mark>$1</mark>');
    };
    const div = document.createElement('div');
    div.className = 'autocomplete-suggestion d-flex align-items-center p-2';
    div.innerHTML = `
      <img src="${h.image || '/static/img/hotel_default.jpg'}" class="rounded me-2" style="width:38px;height:38px;object-fit:cover;box-shadow:0 2px 8px #0002;">
      <div class="flex-grow-1">
        <div class="fw-bold">${highlight(h.name)}</div>
        <div class="small text-muted">${highlight(h.location || '')} ${h.stars ? '· ' + h.stars + '★' : ''} ${h.type ? '· ' + h.type : ''}</div>
      </div>
    `;
    div.onclick = () => {
      window.location.href = `/hotel/${slug}`;
    };
    acBox.appendChild(div);
  });
  acBox.style.display = 'block';
}

function hideAutocompleteSuggestions() {
  const acBox = document.getElementById('autocomplete-suggestions');
  if (acBox) acBox.style.display = 'none';
}

// --- Redefinir renderFilters para input premium y autocompletado ---
function renderFilters(hotels) {
    const filters = document.getElementById('filters');
    const estrellasOpciones = [1, 2, 3, 4, 5];
    filters.innerHTML = `
        <div class="row g-2 align-items-end justify-content-center filters-container-glass">
            <div class="col-md-7">
                <label class="form-label">Buscar hotel o alojamiento</label>
                <div class="input-group input-group-lg position-relative">
                  <span class="input-group-text bg-white border-0"><i class="bi bi-search"></i></span>
                  <input id="buscador-hoteles" type="text" class="form-control buscador-lux" placeholder="Nombre, ubicación, amenities, lujo, playa, jacuzzi, penthouse, etc..." autocomplete="off">
                  <button id="btn-buscar-hoteles" class="btn btn-primary px-4" type="button"><i class="bi bi-magic"></i> Buscar</button>
                </div>
            </div>
            <div class="col-md-3">
                <label class="form-label">Filtrar por estrellas</label>
                <select id="filtro-estrellas" class="form-select">
                    <option value="">Todas</option>
                    ${estrellasOpciones.map(e => `<option value="${e}">${e} estrella${e>1?'s':''}</option>`).join('')}
                </select>
            </div>
        </div>
    `;
    // Inicializar Fuse
    fuse = new Fuse(hotels, fuseOptions);
    // Eventos
    const input = document.getElementById('buscador-hoteles');
    const btnBuscar = document.getElementById('btn-buscar-hoteles');
    input.addEventListener('input', function() {
      const val = this.value.trim();
      if (val.length > 0) {
        const results = fuse.search(val);
        renderAutocompleteSuggestions(results, val);
      } else {
        hideAutocompleteSuggestions();
      }
    });
    input.addEventListener('focus', function() {
      const val = this.value.trim();
      if (val.length > 0) {
        const results = fuse.search(val);
        renderAutocompleteSuggestions(results, val);
      }
    });
    input.addEventListener('blur', function() {
      setTimeout(hideAutocompleteSuggestions, 180);
    });
    // Refuerzo: click SIEMPRE ejecuta filtrarHoteles
    btnBuscar.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Botón buscar presionado');
      filtrarHoteles();
    });
    document.getElementById('filtro-estrellas').addEventListener('change', filtrarHoteles);
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') filtrarHoteles();
    });
    // Event delegation por si el DOM cambia
    filters.addEventListener('click', function(e) {
      if (e.target && e.target.id === 'btn-buscar-hoteles') {
        e.preventDefault();
        console.log('Delegation: Botón buscar presionado');
        filtrarHoteles();
      }
    });
}

function normalizarTexto(texto) {
  return texto
    .toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Quitar tildes
    .replace(/[^a-z0-9\s]/gi, '');
}

// --- Diccionario de palabras clave y sinónimos para amenities, tipo, precio, etc. ---
const keywordMap = {
  // Amenities
  'parqueadero': 'parqueadero', 'parking': 'parqueadero', 'estacionamiento': 'parqueadero',
  'piscina': 'piscina', 'alberca': 'piscina', 'pool': 'piscina',
  'wifi': 'wifi', 'internet': 'wifi',
  'desayuno': 'desayuno', 'breakfast': 'desayuno',
  'gimnasio': 'gimnasio', 'gym': 'gimnasio',
  'spa': 'spa', 'jacuzzi': 'jacuzzi',
  'bar': 'bar', 'restaurante': 'restaurante', 'restaurant': 'restaurante',
  'playa': 'playa', 'beach': 'playa',
  'aire acondicionado': 'aire acondicionado', 'ac': 'aire acondicionado',
  'mascotas': 'mascotas', 'pet': 'mascotas', 'pet friendly': 'mascotas',
  // Tipo
  'hotel': 'hotel', 'hostal': 'hostal', 'apartamento': 'apartamento', 'apartaestudio': 'apartamento', 'casa': 'casa',
  // Precio
  'barato': 'barato', 'económico': 'barato', 'económico': 'barato', 'low cost': 'barato',
  'lujo': 'lujo', 'lujoso': 'lujo', 'premium': 'lujo', 'exclusivo': 'lujo', 'caro': 'lujo',
  // Ubicación
  'centro': 'centro', 'bocagrande': 'bocagrande', 'playa': 'playa', 'mar': 'playa',
  // Otros
  'familiar': 'familiar', 'romántico': 'romántico', 'pareja': 'romántico', 'negocios': 'negocios',
};

const vaguePhrases = [
  'no se', 'no sé', 'sorprendeme', 'sorpréndeme', 'elige por mi', 'elige por mí', 'cualquiera', 'lo que sea', 'no tengo preferencia', 'dame una opción', 'dame opciones', 'sorpréndeme', 'sorprendeme', 'no importa', 'random'
];

// --- Analizador de intención y preferencias ---
function analizarPreferencias(frase) {
  const texto = frase.toLowerCase();
  // 1. Detectar frases vagas
  if (vaguePhrases.some(p => texto.includes(p))) {
    return { tipo: 'vago' };
  }
  // 2. Extraer palabras clave
  let preferencias = { amenities: [], tipo: null, precio: null, ubicacion: null };
  for (const [k, v] of Object.entries(keywordMap)) {
    if (texto.includes(k)) {
      // Amenities
      if ([
        'parqueadero','piscina','wifi','desayuno','gimnasio','spa','jacuzzi','bar','restaurante','playa','aire acondicionado','mascotas'
      ].includes(v) && !preferencias.amenities.includes(v)) {
        preferencias.amenities.push(v);
      }
      // Tipo
      if (['hotel','hostal','apartamento','casa'].includes(v)) preferencias.tipo = v;
      // Precio
      if (['barato','lujo'].includes(v)) preferencias.precio = v;
      // Ubicación
      if (['centro','bocagrande','playa'].includes(v)) preferencias.ubicacion = v;
    }
  }
  return preferencias;
}

// --- Filtro funcional de hoteles con interpretación de intención ---
function filtrarHoteles() {
  const texto = document.getElementById('buscador-hoteles').value.trim();
  const estrellas = document.getElementById('filtro-estrellas').value;
  let filtrados = _hoteles;
  let resultados = [];
  let preferencias = null;

  if (texto) {
    preferencias = analizarPreferencias(texto);
    // Si la frase es vaga, mostrar random/destacados
    if (preferencias && preferencias.tipo === 'vago') {
      filtrados = [..._hoteles].sort((a,b) => (b.rating||0)-(a.rating||0)).slice(0,6);
    } else if (
      preferencias && (
        (preferencias.amenities && preferencias.amenities.length > 0) || preferencias.tipo || preferencias.precio || preferencias.ubicacion
      )
    ) {
      filtrados = _hoteles.filter(h => {
        let ok = true;
        // Amenities (inclusión parcial, no exacta)
        if (preferencias.amenities && preferencias.amenities.length > 0) {
          ok = preferencias.amenities.every(am => (String(h.amenities || '')).toLowerCase().includes(am));
        }
        // Tipo
        if (ok && preferencias.tipo) {
          ok = (h.type||'').toLowerCase().includes(preferencias.tipo);
        }
        // Precio
        if (ok && preferencias.precio === 'barato') {
          ok = (h.price && (h.price.toLowerCase().includes('barato') || h.price.toLowerCase().includes('económico') || h.price.toLowerCase().includes('low')));
        }
        if (ok && preferencias.precio === 'lujo') {
          ok = (h.price && (h.price.toLowerCase().includes('lujo') || h.price.toLowerCase().includes('premium') || h.price.toLowerCase().includes('alto')));
        }
        // Ubicación
        if (ok && preferencias.ubicacion) {
          ok = (h.location||'').toLowerCase().includes(preferencias.ubicacion);
        }
        return ok;
      });
      // Si no hay resultados, usar Fuse.js como fallback
      if (filtrados.length === 0) {
        resultados = fuse.search(texto);
        filtrados = resultados.map(r => r.item);
      }
    } else {
      // Si no se detectan preferencias claras, usar Fuse.js (búsqueda difusa normal)
      resultados = fuse.search(texto);
      filtrados = resultados.map(r => r.item);
    }
  }
  if (estrellas) {
    filtrados = filtrados.filter(h => {
      if (!h.stars) return false;
      const match = String(h.stars).match(/(\d)/);
      return match && match[1] === estrellas;
    });
  }
  // Mostrar/ocultar secciones según si hay búsqueda activa
  const recomendacionesSection = document.querySelector('.recomendaciones-section');
  const todosHotelesSection = document.querySelector('.todos-hoteles-section');
  if (texto || estrellas) {
    if (recomendacionesSection) recomendacionesSection.style.display = 'none';
    if (todosHotelesSection) {
      todosHotelesSection.style.display = 'block';
      const titulo = todosHotelesSection.querySelector('h3');
      if (titulo) {
        let tituloTexto = 'Resultados de búsqueda';
        if (texto) tituloTexto += ` para "${texto}"`;
        if (estrellas) tituloTexto += ` con ${estrellas} estrella${estrellas > 1 ? 's' : ''}`;
        titulo.innerHTML = `<span style=\"color:#0d6efd;\">🔍</span> ${tituloTexto}`;
      }
    }
  } else {
    if (recomendacionesSection) recomendacionesSection.style.display = 'block';
    if (todosHotelesSection) {
      todosHotelesSection.style.display = 'block';
      const titulo = todosHotelesSection.querySelector('h3');
      if (titulo) titulo.innerHTML = '<span style=\"color:#222;\">🏨</span> Todos los hoteles';
    }
  }
  renderHotelCards(filtrados, 'hotels');
  // Mostrar cantidad de resultados con estilo premium
  const container = document.getElementById('hotels');
  const countDiv = document.getElementById('resultados-hoteles');
  if (countDiv) countDiv.remove();
  if (texto || estrellas) {
    const nuevoDiv = document.createElement('div');
    nuevoDiv.id = 'resultados-hoteles';
    nuevoDiv.className = 'col-12 text-center mb-3';
    nuevoDiv.innerHTML = `
      <div class=\"alert alert-info border-0\" style=\"background: linear-gradient(90deg,#e0eafc 0%,#cfdef3 100%); border-radius: 12px;\">
        <i class=\"bi bi-info-circle me-2\"></i>
        <strong>${filtrados.length}</strong> resultado${filtrados.length===1?'':'s'} encontrado${filtrados.length===1?'':'s'}
        ${texto ? ` para \"${texto}\"` : ''}
        ${estrellas ? ` con ${estrellas} estrella${estrellas > 1 ? 's' : ''}` : ''}
      </div>
    `;
    if (container && container.parentNode) {
      container.parentNode.insertBefore(nuevoDiv, container);
    }
  }
  // Feedback visual premium
  if (texto && filtrados.length === 0) {
    Toastify({
      text: "No se encontraron alojamientos con esa búsqueda. ¡Prueba otra frase o preferencia!",
      duration: 3500,
      gravity: "top",
      position: "center",
      backgroundColor: "linear-gradient(90deg,#ff512f,#dd2476)",
      stopOnFocus: true,
      close: true,
      style: { fontWeight: 'bold', fontSize: '1.1em', borderRadius: '12px' }
    }).showToast();
  }
  hideAutocompleteSuggestions();
}

// --- Estilos premium para autocompletado y filtros (Glassmorphism, animaciones) ---