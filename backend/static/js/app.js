  const stories = {
    hachiko: {
      title: 'Hachiko',
      breed: 'Akita Inu',
      subtitle: 'La lealtad no entiende de tiempo',
      bg: 'linear-gradient(135deg, #c6a15b, #5c3a1e)',
      icon: 'fa-solid fa-star',
      fullStory: 'Hachiko nació en 1923 en la prefectura de Akita, Japón. Fue adoptado por el profesor Hidesaburo Ueno, quien viajaba diariamente a la estación de Shibuya. Cada mañana, Hachiko acompañaba a su dueño a la estación y regresaba cada tarde para esperarlo.\n\nEl 21 de mayo de 1925, el profesor Ueno sufrió una hemorragia cerebral en la universidad y nunca regresó a casa. Pero Hachiko siguió yendo a la estación cada día, a la misma hora, esperando el regreso de su amigo.\n\nDurante nueve años, nueve meses y quince días, Hachiko esperó. Los comerciantes locales lo alimentaban y cuidaban. Su historia trascendió fronteras, convirtiéndose en un símbolo mundial de lealtad incondicional.\n\nHoy, una estatua de bronce de Hachiko lo espera para siempre en la estación de Shibuya, y su historia nos recuerda que el verdadero amor no entiende de despedidas.'
    },
    balto: {
      title: 'Balto',
      breed: 'Husky',
      subtitle: 'Un héroe de cuatro patas',
      bg: 'linear-gradient(135deg, #5a7a8a, #2a4a5a)',
      icon: 'fa-solid fa-snowflake',
      fullStory: 'En el invierno de 1925, la ciudad de Nome, Alaska, fue azotada por un brote de difteria. El único suero capaz de salvar a los niños estaba en Anchorage, a más de 1,000 kilómetros de distancia. La única forma de llevarlo era mediante un relevo de trineos tirados por perros.\n\nBalto, un husky siberiano de aspecto tosco pero corazón indomable, lideró el equipo de Gunnar Kaasen en la etapa final del trayecto. En medio de una tormenta de nieve con vientos de más de 80 km/h y temperaturas de -50°C, Balto guió al equipo a través de la oscuridad y el hielo.\n\nCuando finalmente llegaron a Nome, el suero había llegado a tiempo. Balto se convirtió en un héroe nacional, pero su verdadera grandeza no estaba en la fama, sino en la determinación de no rendirse nunca, incluso cuando todo parecía perdido.'
    },
    laika: {
      title: 'Laika',
      breed: 'Pastor Ruso',
      subtitle: 'La primera viajera espacial',
      bg: 'linear-gradient(135deg, #2e3440, #1a1e28)',
      icon: 'fa-solid fa-rocket',
      fullStory: 'Laika era una perra callejera recogida de las calles de Moscú. Pequeña, de mirada dulce, mestiza de pastor ruso. Nadie imaginaba que esta perrita tranquila se convertiría en la primera criatura terrestre en viajar al espacio exterior.\n\nEl 3 de noviembre de 1957, a bordo del Sputnik 2, Laika despegó hacia el cosmos. Su entrenamiento la preparó para soportar las fuerzas G y el confinamiento extremo. En sus primeros días en órbita, los sensores mostraron que Laika estaba tranquila, comiendo su comida especial.\n\nAunque su viaje no tuvo regreso, Laika abrió el camino para la exploración espacial humana. Su legado vive en cada estrella que miramos, recordándonos que los seres más humildes pueden lograr las hazañas más extraordinarias.'
    }
  };



  const FALLBACK_PHRASES = {
    'Pug':'Alegría','Boston Terrier':'Elegancia','Boxer':'Energía','Bull Terrier':'Personalidad',
    'Pastor de Montañas':'Fortaleza','Basset Hound':'Ternura','Yorkshire Terrier':'Carisma',
    'Shar Pei':'Sabiduría','Akita Inu':'Lealtad eterna','Beagle':'Curiosidad','Pastor Alemán':'Coraje y lealtad',
    'Border Collie':'Inteligencia','Bulldog Francés':'Encanto','Bulldog Inglés':'Perseverancia',
    'Cane Corso':'Protección','Chihuahua':'Valentía','Chow Chow':'Dignidad','Corgi Galés':'Alegría',
    'Dálmata':'Elegancia','Dogo Argentino':'Nobleza','Jack Russell':'Aventura','Kangal Turco':'Coraje',
    'Pastor Belga Malinois':'Lealtad','Pitbull Terrier':'Fuerza','Pomerania':'Viveza','Rottweiler':'Confianza',
    'Salchicha':'Persistencia','San Bernardo':'Bondad','Pinscher':'Alerta','Papillon':'Gracia',
    'Terrier Escocés':'Carácter'
  };

  const FALLBACK_BG = {
    'Pug':'#C49A6C','Boston Terrier':'#2A2A2A','Boxer':'#C4956A','Bull Terrier':'#D4B8A0',
    'Pastor de Montañas':'#4A3520','Basset Hound':'#B8956A','Yorkshire Terrier':'#8A9A8A',
    'Shar Pei':'#C4A070','Akita Inu':'#C49A6C','Beagle':'#E8C8A0','Pastor Alemán':'#5C4033',
    'Border Collie':'#2A2A2A','Bulldog Francés':'#C49A6C','Bulldog Inglés':'#8B7355',
    'Cane Corso':'#3A3020','Chihuahua':'#E8CBA0','Chow Chow':'#D4A060','Corgi Galés':'#E8B860',
    'Dálmata':'#FFFFFF','Dogo Argentino':'#F0F0F0','Jack Russell':'#E8D8C0','Kangal Turco':'#8A7A60',
    'Pastor Belga Malinois':'#8A6A40','Pitbull Terrier':'#C4A880','Pomerania':'#E8C880',
    'Rottweiler':'#2A2018','Salchicha':'#B8885A','San Bernardo':'#D4A860','Pinscher':'#2A2018',
    'Papillon':'#E8D8C0','Terrier Escocés':'#4A3A2A'
  };

  function getPhrase(name, lang) {
    if (FALLBACK_PHRASES[name]) return FALLBACK_PHRASES[name];
    const phrases = { es: 'Artesanía única', en: 'Unique craftsmanship', pt: 'Artesanato único', fr: 'Artisanat unique' };
    return phrases[lang] || phrases.en;
  }

  function getBg(name) {
    if (FALLBACK_BG[name]) return FALLBACK_BG[name];
    const colors = ['#C49A6C','#2A2A2A','#C4956A','#D4B8A0','#4A3520','#B8956A','#8A9A8A','#C4A070','#5C4033','#8B7355','#3A3020','#E8CBA0','#D4A060','#E8B860','#FFFFFF','#E8D8C0','#8A7A60','#C4A880','#2A2018','#B8885A','#D4A860'];
    let h = 0;
    for (let i = 0; i < name.length; i++) h = ((h << 5) - h) + name.charCodeAt(i);
    return colors[Math.abs(h) % colors.length];
  }

  /* Cache de productos por categoría */
  let productsCache = {};
  var categoryState = {};
  var galleryProducts = {};

  function getPageKey(gridId) { return gridId + '_page'; }

  function isLatestCategoryRequest(gridId, requestId) {
    return !!categoryState[gridId] && categoryState[gridId].requestId === requestId;
  }

  async function loadCategoryProducts(gridId, categoryId, page) {
    var lang = currentLang || 'es';
    page = page || 1;
    var cacheKey = lang + '_c' + categoryId + '_p' + page;
    var grid = document.getElementById(gridId);
    if (!grid) return;

    var prev = categoryState[gridId];
    var isInitial = !prev || !prev.currentPage;
    var requestId = (prev && prev.requestId || 0) + 1;

    categoryState[gridId] = {
      loading: true,
      currentPage: page,
      requestId: requestId,
      totalPages: (prev && prev.totalPages) || 1
    };

    if (isInitial) {
      grid.innerHTML = '<div class="catalog-loading"><i class="fa-solid fa-paw"></i>Cargando productos...</div>';
    }

    if (productsCache[cacheKey]) {
      var cached = productsCache[cacheKey];
      if (isLatestCategoryRequest(gridId, requestId)) {
        renderCategoryProducts(gridId, cached.items, cached.count, page, categoryId);
      }
      if (categoryState[gridId] && categoryState[gridId].requestId === requestId) {
        categoryState[gridId].loading = false;
      }
      return;
    }

    try {
      var res = await fetch('/api/products/?language=' + lang + '&category=' + categoryId + '&page=' + page + '&page_size=8');
      var json = await res.json();
      var items = json.results || json;
      var count = json.count || items.length;
      productsCache[cacheKey] = { items: items, count: count };
      if (isLatestCategoryRequest(gridId, requestId)) {
        renderCategoryProducts(gridId, items, count, page, categoryId);
      }
    } catch (e) {
      console.error('[IOQUE] Error loading category ' + categoryId + ':', e);
      if (isLatestCategoryRequest(gridId, requestId)) {
        grid.innerHTML = '<div class="catalog-empty"><i class="fa-solid fa-paw"></i>Error al cargar</div>';
      }
    }
    if (categoryState[gridId] && categoryState[gridId].requestId === requestId) {
      categoryState[gridId].loading = false;
    }
  }

  function changeCategoryPage(gridId, categoryId, delta) {
    var state = categoryState[gridId] || {};
    var currentPage = state.currentPage || 1;
    var totalPages = state.totalPages || 1;
    var next = currentPage + delta;
    if (next < 1 || next > totalPages) return;
    loadCategoryProducts(gridId, categoryId, next);
  }

  function renderCategoryProducts(gridId, items, count, page, categoryId) {
    var grid = document.getElementById(gridId);
    if (!grid) return;
    var totalPages = Math.ceil(count / 8) || 1;
    if (!categoryState[gridId]) categoryState[gridId] = {};
    categoryState[gridId].currentPage = page;
    categoryState[gridId].totalPages = totalPages;

    if (!items || items.length === 0) {
      var msgs = { es: 'No hay productos disponibles', en: 'No products available', pt: 'Nenhum produto disponível', fr: 'Aucun produit disponible' };
      grid.innerHTML = '<div class="catalog-empty"><i class="fa-solid fa-paw"></i>' + (msgs[currentLang] || msgs.en) + '</div>';
      return;
    }
    var html = '';
    items.forEach(function(p, i) {
      var delay = Math.min(i * 0.03, 0.6).toFixed(2);
      var realImg = null, keyImg = null;
      if (p.images && p.images.length) {
        realImg = p.images.find(function(img) { return img.type === 'REAL'; }) || null;
        keyImg = p.images.find(function(img) { return img.type === 'KEYCHAIN'; }) || null;
      }
      var nokey = !keyImg, nobreed = !realImg;
      var crossfade = !nokey && !nobreed ? 'crossfade' : '';
      var frontSrc = (realImg && realImg.thumbnail) ? realImg.thumbnail : (realImg ? realImg.url : (keyImg && keyImg.thumbnail ? keyImg.thumbnail : (keyImg ? keyImg.url : '')));
      var backSrc = (keyImg && keyImg.thumbnail) ? keyImg.thumbnail : (keyImg ? keyImg.url : '');
      var name = p.name || 'Producto';
      var phrase = getPhrase(name, currentLang);
      var bg = getBg(name);
      var imgCount = (p.images && p.images.length) ? p.images.length : 0;
      galleryProducts[p.id] = p;
      html += '<div class="product-card reveal" style="transition-delay:' + delay + 's">'
        + '<div class="product-img-wrap' + (crossfade ? ' crossfade' : '') + '">'
        + '<img src="' + frontSrc + '" alt="' + name + '" class="product-img" loading="lazy" width="400" height="400" onerror="this.style.background=\'' + bg + '\';this.style.display=\'block\'">'
        + (backSrc && !nokey ? '<img src="' + backSrc + '" alt="' + name + '" class="product-img-back" loading="lazy" width="400" height="400" onerror="this.style.display=\'none\'">' : '')
        + (imgCount > 0 ? '<button class="gallery-btn" data-product-id="' + p.id + '" aria-label="Ver galería de ' + name + '"><i class="fa-solid fa-camera"></i><span class="gallery-btn-count">+' + imgCount + '</span></button>' : '')
        + '</div>'
        + '<div class="product-info">'
        + '<div class="product-header"><span class="product-name">' + name + '</span><span class="product-price">$' + (p.price || 0).toLocaleString('es-CO') + '</span></div>'
        + '<p class="product-phrase">"' + phrase + '"</p>'
        + '<button onclick="addToCart(' + (p.id || 0) + ',\'' + name.replace(/'/g,"\\'") + '\',' + (p.price || 0) + ',this,\'' + (frontSrc || '').replace(/'/g,"\\'") + '\',\'' + (p.category_name || '').replace(/'/g,"\\'") + '\')" class="btn-gold-border"><i class="fa-solid fa-plus"></i> ' + ({ es: 'Añadir', en: 'Add', pt: 'Adicionar', fr: 'Ajouter' }[currentLang] || 'Add') + '</button>'
        + '</div></div>';
    });
    grid.innerHTML = html;
    var pag = document.getElementById(gridId + '-pagination');
    if (pag) {
      if (totalPages > 1) {
        pag.style.display = 'flex';
        var prevBtn = document.getElementById(gridId + '-prev');
        var nextBtn = document.getElementById(gridId + '-next');
        var info = document.getElementById(gridId + '-page-info');
        if (prevBtn) prevBtn.disabled = page <= 1;
        if (nextBtn) nextBtn.disabled = page >= totalPages;
        if (info) {
          var pageMsgs = { es: 'P\u00E1gina ' + page + ' de ' + totalPages, en: 'Page ' + page + ' of ' + totalPages, pt: 'P\u00E1gina ' + page + ' de ' + totalPages, fr: 'Page ' + page + ' sur ' + totalPages };
          info.textContent = pageMsgs[currentLang] || pageMsgs.en;
        }
      } else {
        pag.style.display = 'none';
      }
    }
    setTimeout(handleReveal, 100);
  }

  function loadAllCategories() {
    loadCategoryProducts('catalog-grid', 1);
    loadCategoryProducts('religion-grid', 3);
    loadCategoryProducts('cuyes-grid', 4);
  }

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.btn-pagination[data-grid]');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    changeCategoryPage(btn.dataset.grid, parseInt(btn.dataset.cat, 10), parseInt(btn.dataset.dir, 10));
  });

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.gallery-btn');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    var productId = parseInt(btn.dataset.productId, 10);
    openGallery(productId, 0);
  });

  let cart = [];
  let paymentState = null;

  const NEQUI_QR_IMAGE = ''; // Ruta/URL configurable del QR de pago. Ej: '/static/img/nequi-qr.png'

  // Envío incluido en el precio del producto + descuento por productos adicionales (espejo del backend)
  const SHIPPING_DISCOUNT_THRESHOLD = 2;
  const SHIPPING_DISCOUNT_PER_EXTRA = 15000;

  function getShippingDiscount(count) {
    if (count > SHIPPING_DISCOUNT_THRESHOLD) {
      return (count - SHIPPING_DISCOUNT_THRESHOLD) * SHIPPING_DISCOUNT_PER_EXTRA;
    }
    return 0;
  }

  function toggleCart() {
    const o = document.getElementById('cart-overlay');
    const s = document.getElementById('cart-sidebar');
    o.classList.toggle('active');
    s.classList.toggle('active');
    document.body.style.overflow = o.classList.contains('active') ? 'hidden' : '';
  }

  function renderNequiQr(qrUrl) {
    const qr = document.getElementById('nequi-qr');
    if (!qr) return;
    const src = qrUrl || NEQUI_QR_IMAGE;
    if (src) {
      qr.innerHTML = '<img src="' + src + '" alt="QR de pago Nequi" class="nequi-qr-img">';
      qr.classList.remove('nequi-qr-placeholder');
      qr.classList.add('nequi-qr-real');
    } else {
      qr.innerHTML = '<i class="fa-solid fa-qrcode"></i><span>' + ((translations[currentLang] && translations[currentLang].pay_qr_placeholder) || 'QR DE PAGO') + '</span>';
      qr.classList.add('nequi-qr-placeholder');
      qr.classList.remove('nequi-qr-real');
    }
  }

  function addToCart(productId, name, price, btn, img, type) {
    const existing = cart.find(i => i.name === name);
    if (existing) existing.qty += 1;
    else cart.push({ productId: productId || 0, name, price, qty: 1, img: img || '', type: type || '' });
    renderCart();
    showToast('✓ ' + name + (currentLang === 'es' ? ' añadido' : ' added'));
    animateCartBadge();
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-check"></i> OK';
      btn.classList.add('btn-added');
      setTimeout(() => { btn.innerHTML = orig; btn.classList.remove('btn-added'); }, 1200);
    }
  }

  function removeFromCart(name) {
    cart = cart.filter(i => i.name !== name);
    renderCart();
    animateCartBadge();
  }

  function updateQty(name, delta) {
    const item = cart.find(i => i.name === name);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) removeFromCart(name);
    else {
      renderCart();
      animateCartBadge();
      const qtyEl = document.querySelector('.cart-qty span[data-name="' + name.replace(/"/g, '\\"') + '"]');
      if (qtyEl) {
        qtyEl.classList.remove('qty-bump');
        void qtyEl.offsetWidth;
        qtyEl.classList.add('qty-bump');
      }
    }
  }

  function animateCartBadge() {
    const nav = document.getElementById('cart-count-nav');
    const fab = document.getElementById('fab-count');
    [nav, fab].forEach(function(el) {
      if (!el) return;
      el.classList.remove('badge-pulse');
      void el.offsetWidth;
      el.classList.add('badge-pulse');
    });
  }

  function formatCOP(value) {
    return '$' + (value || 0).toLocaleString('es-CO');
  }

  function renderCart() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    const subtotalEl = document.getElementById('cart-subtotal');
    const subtotal = cart.reduce((s, i) => s + i.price * i.qty, 0);
    const count = cart.reduce((s, i) => s + i.qty, 0);
    const discount = getShippingDiscount(count);
    const shipping = 0;
    const total = subtotal + shipping - discount;
    const navCount = document.getElementById('cart-count-nav');
    const navTotal = document.getElementById('cart-nav-total');
    const fabCount = document.getElementById('fab-count');
    const fabTotal = document.getElementById('fab-total');
    const fabBtn = document.getElementById('fab-cart');
    if (navCount) navCount.textContent = count;
    if (navTotal) navTotal.textContent = formatCOP(total);
    if (fabCount) fabCount.textContent = '(' + count + ')';
    if (fabTotal) fabTotal.textContent = formatCOP(total);
    if (fabBtn) fabBtn.classList.toggle('has-items', count > 0);

    const t = translations[currentLang];
    const shippingLabel = t.cart_shipping_included || 'Incluido';

    if (cart.length === 0) {
      container.innerHTML = '<div class="cart-empty"><i class="fa-solid fa-bag-shopping"></i><p style="font-size:var(--text-base);">' + t.cart_empty + '</p><p style="font-size:var(--text-sm);margin-top:var(--space-2);">' + t.cart_empty_sub + '</p></div>';
      if (totalEl) totalEl.innerHTML = '$0';
      if (subtotalEl) subtotalEl.textContent = '$0';
      const shippingEl = document.getElementById('cart-shipping');
      if (shippingEl) shippingEl.textContent = shippingLabel;
      const discRow = document.getElementById('cart-discount-row');
      if (discRow) discRow.style.display = 'none';
      return;
    }

    let html = '';
    cart.forEach(i => {
      const lineTotal = i.price * i.qty;
      const thumb = i.img
        ? '<img src="' + i.img + '" alt="' + i.name + '" class="cart-item-thumb">'
        : '<div class="cart-item-avatar">' + i.name.charAt(0) + '</div>';
      const typeLabel = i.type ? '<div class="cart-item-type">' + i.type + '</div>' : '';
      html += '<div class="cart-item">'
        + thumb
        + '<div class="cart-item-info">'
        + '<div class="cart-item-name">' + i.name + '</div>'
        + typeLabel
        + '<div class="cart-item-unit">' + formatCOP(i.price) + (currentLang === 'es' ? ' c/u' : ' ea') + '</div>'
        + '</div>'
        + '<div class="cart-item-right">'
        + '<div class="cart-qty">'
        + '<button onclick="updateQty(\'' + i.name.replace(/'/g,"\\'") + '\',-1)" aria-label="Disminuir">−</button>'
        + '<span data-name="' + i.name.replace(/"/g, '&quot;') + '">' + i.qty + '</span>'
        + '<button onclick="updateQty(\'' + i.name.replace(/'/g,"\\'") + '\',1)" aria-label="Aumentar">+</button>'
        + '</div>'
        + '<div class="cart-item-total">'
        + '<div class="cart-item-price">' + formatCOP(lineTotal) + '</div>'
        + '<button onclick="removeFromCart(\'' + i.name.replace(/'/g,"\\'") + '\')" class="cart-item-remove"><i class="fa-solid fa-trash-can"></i> ' + (currentLang === 'es' ? 'Eliminar' : 'Remove') + '</button>'
        + '</div>'
        + '</div>'
        + '</div>';
    });
    container.innerHTML = html;
    if (subtotalEl) subtotalEl.textContent = formatCOP(subtotal);
    const shippingEl = document.getElementById('cart-shipping');
    if (shippingEl) shippingEl.textContent = shippingLabel;
    const discRow = document.getElementById('cart-discount-row');
    const discEl = document.getElementById('cart-discount');
    if (discount > 0) {
      if (discRow) discRow.style.display = '';
      if (discEl) discEl.textContent = '- ' + formatCOP(discount);
    } else {
      if (discRow) discRow.style.display = 'none';
    }
    if (totalEl) totalEl.innerHTML = formatCOP(total) + ' <small>' + (t.cart_currency || 'COP') + '</small>';
  }

  function t(key, fallback) {
    return (translations[currentLang] && translations[currentLang][key]) || fallback || '';
  }

  function setPaymentStep(step) {
    const checkout = document.getElementById('pay-checkout');
    const qrStep = document.getElementById('pay-qr-step');
    const okStep = document.getElementById('pay-success-step');
    const payBtn = document.getElementById('nequi-pay-btn');
    if (step === 'qr') {
      if (qrStep) qrStep.style.display = '';
      if (okStep) okStep.style.display = 'none';
      if (payBtn) payBtn.style.display = 'none';
    } else if (step === 'success') {
      if (qrStep) qrStep.style.display = 'none';
      if (okStep) okStep.style.display = '';
      if (payBtn) payBtn.style.display = 'none';
    } else {
      if (qrStep) qrStep.style.display = 'none';
      if (okStep) okStep.style.display = 'none';
      if (payBtn) payBtn.style.display = '';
    }
  }

  function cancelPayment() {
    stopPaymentPolling();
    paymentState = null;
    const statusLine = document.getElementById('pay-status-line');
    if (statusLine) statusLine.style.display = 'none';
    const qr = document.getElementById('nequi-qr');
    if (qr) qr.innerHTML = '';
    const statusMsg = document.getElementById('nequi-status-msg');
    if (statusMsg) statusMsg.innerHTML = '';
    setPaymentStep('default');
    resetPayButton();
  }

  function resetPayButton() {
    const payBtn = document.getElementById('nequi-pay-btn');
    if (payBtn) {
      payBtn.disabled = false;
      payBtn.innerHTML = '<i class="fa-solid fa-mobile-screen-button"></i> <span>' + t('pay_nequi_btn', 'IR A PAGAR CON NEQUI') + '</span>';
    }
  }

  function stopPaymentPolling() {
    if (paymentState && paymentState.poll) {
      clearInterval(paymentState.poll);
      paymentState.poll = null;
    }
  }

  async function processPayment() {
    if (cart.length === 0) {
      showToast('❌ ' + t('cart_empty', 'Empty cart'));
      return;
    }

    stopPaymentPolling();

    const statusMsg = document.getElementById('nequi-status-msg');
    const payBtn = document.getElementById('nequi-pay-btn');
    const t0 = t('pay_creating', 'Generando tu pedido...');

    payBtn.disabled = true;
    payBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> ' + t('pay_creating', 'Generando pedido...');
    if (statusMsg) statusMsg.innerHTML = '<span style="color:var(--accent);">' + t0 + '</span>';
    setPaymentStep('default');

    const idempotencyKey = 'client-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);

    try {
      const orderRes = await fetch('/api/orders/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: cart.map(i => ({ product_id: i.productId, quantity: i.qty })),
          idempotency_key: idempotencyKey,
        }),
      });
      const orderData = await orderRes.json();

      if (!orderRes.ok) {
        throw new Error(orderData.error || t('pay_error', 'Error al crear el pedido'));
      }

      const orderNumber = orderData.order_number;

      const qrRes = await fetch('/api/orders/' + orderNumber + '/payment/nequi/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const qrData = await qrRes.json();

      if (!qrRes.ok) {
        throw new Error(qrData.error || t('pay_error_qr', 'No fue posible generar el pago'));
      }

      setPaymentStep('qr');
      renderNequiQr(qrData.qr_code || '');
      if (statusMsg) statusMsg.innerHTML = '';

      paymentState = { orderNumber: orderNumber, poll: null, attempts: 0 };
      pollPaymentStatus(orderNumber);
     } catch (e) {
      if (statusMsg) statusMsg.innerHTML = '<span style="color:#ef4444;">❌ ' + e.message + '</span>';
      setPaymentStep('default');
      resetPayButton();
    }
  }

  function pollPaymentStatus(orderNumber) {
    const statusLine = document.getElementById('pay-status-line');
    const statusMsg = document.getElementById('nequi-status-msg');

    paymentState.attempts = 0;
    paymentState.poll = setInterval(async () => {
      paymentState.attempts++;
      try {
        const res = await fetch('/api/orders/' + orderNumber + '/payment/status/');
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Error de estado');

        const payStatus = data.payment_status;
        const terminal = ['APPROVED', 'REJECTED', 'EXPIRED', 'CANCELLED', 'ERROR', 'REVERSED'];

        if (payStatus === 'APPROVED') {
          stopPaymentPolling();
          setPaymentStep('success');
          const orderEl = document.getElementById('pay-success-order');
          if (orderEl) orderEl.textContent = t('pay_order_label', 'Pedido') + ' #' + data.order_number;
          showToast('✅ ' + t('pay_paid', 'Pago confirmado'));
          cart = [];
          renderCart();
          animateCartBadge();
          return;
        }

        if (terminal.indexOf(payStatus) !== -1) {
          stopPaymentPolling();
          if (statusMsg) {
            let msg;
            if (payStatus === 'EXPIRED') msg = '⏱️ ' + t('pay_expired', 'El pago expiró, intenta de nuevo');
            else if (payStatus === 'ERROR' || payStatus === 'REVERSED') msg = '❌ ' + t('pay_error_final', 'Error en el pago');
            else msg = '❌ ' + t('pay_rejected', 'Pago rechazado');
            statusMsg.innerHTML = '<span style="color:#ef4444;">' + msg + '</span>';
          }
          setPaymentStep('default');
          resetPayButton();
          return;
        }

        if (statusLine) statusLine.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> ' + t('pay_waiting', 'Esperando confirmación del pago...');
      } catch (e) {
        // continue polling
      }

      if (paymentState.attempts >= 60) {
        stopPaymentPolling();
        paymentState = null;
        if (statusLine) statusLine.innerHTML = '<i class="fa-solid fa-clock"></i> ' + t('pay_timeout', 'El tiempo de espera se agotó');
        setPaymentStep('default');
        resetPayButton();
      }
    }, 5000);
  }

  function openStory(id) {
    const s = stories[id];
    if (!s) return;
    const modal = document.getElementById('story-modal');
    const content = document.getElementById('story-content');
    const paras = s.fullStory.split('\n\n').map(p => '<p>' + p + '</p>').join('');
    content.innerHTML =
      '<div class="modal-header" style="background:' + s.bg + ';">'
      + '<div class="modal-header-overlay"></div>'
      + '<i class="' + s.icon + ' modal-header-icon"></i>'
      + '<div class="modal-header-text">'
      + '<span class="modal-header-breed">' + s.breed + '</span>'
      + '<h3 class="modal-header-title">' + s.title + '</h3>'
      + '</div>'
      + '<div class="modal-header-qr"><i class="fa-solid fa-qrcode"></i></div>'
      + '</div>'
      + '<div class="modal-body">'
      + '<p class="modal-italics">"' + s.subtitle + '"</p>'
      + '<div class="modal-body-divider"></div>'
      + paras
      + '<div class="modal-qr-box">'
      + '<i class="fa-solid fa-qrcode"></i>'
      + '<div><p>' + (currentLang === 'es' ? '<strong>¿Tienes el empaque?</strong> Escanea el QR para más contenido exclusivo.' : '<strong>Have the packaging?</strong> Scan the QR for exclusive content.') + '</p></div>'
      + '</div>'
      + '</div>';
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeStory() {
    document.getElementById('story-modal').classList.remove('active');
    document.body.style.overflow = '';
  }

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove('show'), 3000);
  }

  /* ── Gallery Lightbox ── */
  var galleryState = { open: false, productId: null, images: [], index: 0, touchStartX: 0 };

  function openGallery(productId, startIndex) {
    var product = galleryProducts[productId];
    if (!product || !product.images || !product.images.length) return;
    var images = product.images.slice().sort(function(a, b) { return a.sort_order - b.sort_order; });
    galleryState = { open: true, productId: productId, images: images, index: startIndex || 0, touchStartX: 0 };
    var overlay = document.getElementById('gallery-lightbox');
    var titleEl = overlay.querySelector('.lightbox-title');
    var countEl = overlay.querySelector('.lightbox-count');
    titleEl.textContent = product.name || 'Producto';
    countEl.textContent = images.length + ' imagen' + (images.length !== 1 ? 'es' : '');
    renderLightboxImage();
    renderLightboxThumbs();
    overlay.classList.add('active');
    document.body.classList.add('lightbox-open');
    document.body.style.overflow = 'hidden';
  }

  function closeGallery() {
    var overlay = document.getElementById('gallery-lightbox');
    overlay.classList.remove('active');
    document.body.classList.remove('lightbox-open');
    document.body.style.overflow = '';
    galleryState.open = false;
  }

  function navigateGallery(direction) {
    if (!galleryState.open) return;
    var len = galleryState.images.length;
    if (len <= 1) return;
    galleryState.index = (galleryState.index + direction + len) % len;
    renderLightboxImage();
    renderLightboxThumbs();
  }

  function selectThumbnail(index) {
    if (!galleryState.open) return;
    galleryState.index = index;
    renderLightboxImage();
    renderLightboxThumbs();
  }

  function renderLightboxImage() {
    var overlay = document.getElementById('gallery-lightbox');
    var img = overlay.querySelector('.lightbox-image');
    var data = galleryState.images[galleryState.index];
    if (!data) return;
    var src = data.medium || data.url || data.thumbnail || '';
    img.style.opacity = '0';
    setTimeout(function() {
      img.src = src;
      img.alt = data.alt || 'Imagen de producto';
      img.onload = function() { img.style.opacity = '1'; };
      if (img.complete) img.style.opacity = '1';
    }, 100);
    var prevBtn = overlay.querySelector('.lightbox-prev');
    var nextBtn = overlay.querySelector('.lightbox-next');
    if (prevBtn) prevBtn.style.display = galleryState.images.length <= 1 ? 'none' : '';
    if (nextBtn) nextBtn.style.display = galleryState.images.length <= 1 ? 'none' : '';
  }

  function renderLightboxThumbs() {
    var overlay = document.getElementById('gallery-lightbox');
    var container = overlay.querySelector('.lightbox-thumbnails');
    var html = '';
    galleryState.images.forEach(function(img, i) {
      var src = img.thumbnail || img.url || '';
      var active = i === galleryState.index ? ' active' : '';
      html += '<img class="lightbox-thumb' + active + '" src="' + src + '" alt="' + (img.alt || 'Miniatura') + '" onclick="selectThumbnail(' + i + ')" loading="lazy">';
    });
    container.innerHTML = html;
    var activeThumb = container.querySelector('.lightbox-thumb.active');
    if (activeThumb) activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }

  (function() {
    var wrap = document.querySelector('.lightbox-image-wrap');
    if (!wrap) return;
    wrap.addEventListener('touchstart', function(e) {
      galleryState.touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });
    wrap.addEventListener('touchend', function(e) {
      var delta = e.changedTouches[0].clientX - galleryState.touchStartX;
      if (Math.abs(delta) > 50) {
        navigateGallery(delta > 0 ? -1 : 1);
      }
    }, { passive: true });
  })();

  function toggleMobileMenu() {
    document.getElementById('mobile-menu').classList.toggle('open');
  }

  function closeMobileMenu() {
    document.getElementById('mobile-menu').classList.remove('open');
  }

  function handleReveal() {
    document.querySelectorAll('.reveal').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight * 0.85) el.classList.add('visible');
    });
  }

  window.addEventListener('scroll', handleReveal);
  window.addEventListener('load', handleReveal);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (galleryState.open) closeGallery();
      else if (document.getElementById('story-modal').classList.contains('active')) closeStory();
      else if (document.getElementById('cart-overlay').classList.contains('active')) toggleCart();
    }
    if (galleryState.open) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); navigateGallery(-1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); navigateGallery(1); }
    }
  });

  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── Translations ── */
  const translations = {
    es: {
      nav_esencia: 'Esencia', nav_catalogo: 'Catálogo', nav_historias: 'Historias', nav_contacto: 'Contacto',
      theme_toggle: 'Tema',
      hero_badge: 'Edición Limitada · Hecho a Mano', hero_subtitle: 'Artesanias',
      hero_tagline: '"El lazo que nos une"',
      hero_text: 'Cuero · Hilo · Aguja · Cada llavero es una pieza única de arte portable.',
      hero_explorar: 'Explorar', hero_historias_btn: 'Historias',
      social_instagram: 'Instagram', social_tiktok: 'TikTok', social_youtube: 'YouTube', social_facebook: 'Facebook',
      esencia_label: '// 001', esencia_title: 'La <span style="color:var(--accent);">materia</span> del arte',
      esencia_desc: 'No hay dos piezas iguales. Cada llavero es el resultado de un diálogo entre la mano y la materia.',
      esencia_valor1_title: 'Cuero', esencia_valor1_text: 'Seleccionado, cortado, trabajado. Cada pieza cuenta su propia historia antes de ser llavero.',
      esencia_valor2_title: 'Hilo', esencia_valor2_text: 'Encerado, resistente. Cada puntada es deliberada, como cada palabra en una carta escrita a mano.',
      esencia_valor3_title: 'Alma', esencia_valor3_text: 'Cada raza tiene un espíritu. Capturamos ese gesto, esa mirada, esa energía inconfundible.',
      proceso_cortar: 'Cortar', proceso_coser: 'Coser', proceso_montar: 'Montar', proceso_empacar: 'Empacar',
      catalogo_label: '// 002', catalogo_title: 'Galería <span style="color:var(--accent);">Mascotas</span>',
      catalogo_desc: 'Una colección de retratos en cuero. Cada uno con su propia frecuencia.',
      anadir: 'Añadir',
      historias_label: '// 003', historias_title: 'Leyendas <span style="color:var(--accent);">con patas</span>',
      historias_desc: 'Perros que cambiaron el mundo. Uno a su manera.',
      cart_title: 'Mi Carrito', cart_empty: 'Vacío', cart_empty_sub: 'Agrega productos del catálogo',
      cart_subtotal: 'Subtotal', cart_shipping: 'Envío', cart_shipping_included: 'Incluido', cart_currency: 'COP',
      cart_total: 'TOTAL', cart_discount: 'Descuento',
      nav_cart: 'Carrito', fab_text: 'VER MI PEDIDO',
      pay_nequi_btn: 'IR A PAGAR CON NEQUI',
      pay_qr_title: 'Escanea para pagar con Nequi', pay_qr_placeholder: 'QR DE PAGO', pay_qr_hint: 'Abre Nequi y escanea el código',
      pay_cancel: 'Cancelar y seguir comprando',
      pay_nequi_account: 'Cuenta Nequi:',
      pay_creating: 'Generando tu pedido...', pay_error: 'Error al crear el pedido', pay_error_qr: 'No fue posible generar el pago', pay_error_final: 'Error en el pago',
      pay_step_order: 'Tu pedido', pay_step_scan: 'Escanea', pay_step_done: 'Confirmación',
      pay_waiting: 'Esperando confirmación del pago...', pay_timeout: 'El tiempo de espera se agotó',
      pay_paid: 'Pago confirmado', pay_rejected: 'Pago rechazado', pay_expired: 'El pago expiró, intenta de nuevo',
      pay_success: '¡Pago confirmado!', pay_success_text: 'Gracias por comprar en IO QUE Artesanías.',
      pay_order_label: 'Pedido',
      pay_mp_text: 'Elige tu método de pago.', pay_mp_btn: 'Pagar',
      pay_secure: 'Pago seguro',
      footer_desc: 'Artesanía en cuero. Hecho a mano desde Colombia.',
      footer_nav: 'Navegación', footer_inicio: 'Inicio',
      footer_redes: 'Redes', footer_contacto: 'Contacto', footer_pagos: 'Pagos',
      footer_copy: '&copy; 2026 IOQUE · Hecho a mano',
      footer_terminos: 'Términos', footer_privacidad: 'Privacidad', footer_envios: 'Envíos'
    },
    en: {
      nav_esencia: 'Essence', nav_catalogo: 'Catalog', nav_historias: 'Stories', nav_contacto: 'Contact',
      theme_toggle: 'Theme',
      hero_badge: 'Limited Edition · Handmade', hero_subtitle: 'Artesanias',
      hero_tagline: '"The bond that unites us"',
      hero_text: 'Leather · Thread · Needle · Each keychain is a unique piece of portable art.',
      hero_explorar: 'Explore', hero_historias_btn: 'Stories',
      social_instagram: 'Instagram', social_tiktok: 'TikTok', social_youtube: 'YouTube', social_facebook: 'Facebook',
      esencia_label: '// 001', esencia_title: 'The <span style="color:var(--accent);">matter</span> of art',
      esencia_desc: 'No two pieces are alike. Each keychain is the result of a dialogue between hand and material.',
      esencia_valor1_title: 'Leather', esencia_valor1_text: 'Selected, cut, worked. Each piece tells its own story before becoming a keychain.',
      esencia_valor2_title: 'Thread', esencia_valor2_text: 'Waxed, durable. Every stitch is deliberate, like every word in a handwritten letter.',
      esencia_valor3_title: 'Soul', esencia_valor3_text: 'Every breed has a spirit. We capture that gesture, that look, that unmistakable energy.',
      proceso_cortar: 'Cut', proceso_coser: 'Sew', proceso_montar: 'Assemble', proceso_empacar: 'Pack',
      catalogo_label: '// 002', catalogo_title: '<span style="color:var(--accent);">Mascotas</span> Gallery',
      catalogo_desc: 'A collection of leather portraits. Each with its own frequency.',
      anadir: 'Add',
      historias_label: '// 003', historias_title: 'Legends <span style="color:var(--accent);">on paws</span>',
      historias_desc: 'Dogs that changed the world. Each in their own way.',
      cart_title: 'My Cart', cart_empty: 'Empty', cart_empty_sub: 'Add products from the catalog',
      cart_subtotal: 'Subtotal', cart_shipping: 'Shipping', cart_shipping_included: 'Included', cart_currency: 'COP',
      cart_total: 'TOTAL', cart_discount: 'Discount',
      nav_cart: 'Cart', fab_text: 'VIEW MY ORDER',
      pay_nequi_btn: 'PAY WITH NEQUI',
      pay_qr_title: 'Scan to pay with Nequi', pay_qr_placeholder: 'PAYMENT QR', pay_qr_hint: 'Open Nequi and scan the code',
      pay_cancel: 'Cancel and keep shopping',
      pay_nequi_account: 'Nequi account:',
      pay_creating: 'Generating your order...', pay_error: 'Error creating the order', pay_error_qr: 'Could not generate the payment', pay_error_final: 'Payment error',
      pay_step_order: 'Your order', pay_step_scan: 'Scan', pay_step_done: 'Confirmation',
      pay_waiting: 'Waiting for payment confirmation...', pay_timeout: 'The wait timed out',
      pay_paid: 'Payment confirmed', pay_rejected: 'Payment rejected', pay_expired: 'Payment expired, try again',
      pay_success: 'Payment confirmed!', pay_success_text: 'Thank you for shopping at IO QUE Artesanías.',
      pay_order_label: 'Order',
      pay_mp_text: 'Choose your payment method.', pay_mp_btn: 'Pay',
      pay_secure: 'Secure payment',
      footer_desc: 'Leather craftsmanship. Handmade from Colombia.',
      footer_nav: 'Navigation', footer_inicio: 'Home',
      footer_redes: 'Social', footer_contacto: 'Contact', footer_pagos: 'Payments',
      footer_copy: '&copy; 2026 IOQUE · Handmade',
      footer_terminos: 'Terms', footer_privacidad: 'Privacy', footer_envios: 'Shipping'
    },
    pt: {
      nav_esencia: 'Essência', nav_catalogo: 'Catálogo', nav_historias: 'Histórias', nav_contacto: 'Contato',
      theme_toggle: 'Tema',
      hero_badge: 'Edição Limitada · Feito à Mão', hero_subtitle: 'Artesanias',
      hero_tagline: '"O laço que nos une"',
      hero_text: 'Couro · Linha · Agulha · Cada chaveiro é uma peça única de arte portátil.',
      hero_explorar: 'Explorar', hero_historias_btn: 'Histórias',
      social_instagram: 'Instagram', social_tiktok: 'TikTok', social_youtube: 'YouTube', social_facebook: 'Facebook',
      esencia_label: '// 001', esencia_title: 'A <span style="color:var(--accent);">matéria</span> da arte',
      esencia_desc: 'Não há duas peças iguais. Cada chaveiro é o resultado de um diálogo entre a mão e a matéria.',
      esencia_valor1_title: 'Couro', esencia_valor1_text: 'Selecionado, cortado, trabalhado. Cada peça conta sua própria história antes de se tornar um chaveiro.',
      esencia_valor2_title: 'Linha', esencia_valor2_text: 'Encerada, resistente. Cada ponto é deliberado, como cada palavra em uma carta escrita à mão.',
      esencia_valor3_title: 'Alma', esencia_valor3_text: 'Cada raça tem um espírito. Capturamos esse gesto, esse olhar, essa energia inconfundível.',
      proceso_cortar: 'Cortar', proceso_coser: 'Costurar', proceso_montar: 'Montar', proceso_empacar: 'Empacotar',
      catalogo_label: '// 002', catalogo_title: 'Galeria <span style="color:var(--accent);">Animais</span>',
      catalogo_desc: 'Uma coleção de retratos em couro. Cada um com sua própria frequência.',
      anadir: 'Adicionar',
      historias_label: '// 003', historias_title: 'Lendas <span style="color:var(--accent);">de patas</span>',
      historias_desc: 'Cães que mudaram o mundo. Cada um à sua maneira.',
      cart_title: 'Meu Carrinho', cart_empty: 'Vazio', cart_empty_sub: 'Adicione produtos do catálogo',
      cart_subtotal: 'Subtotal', cart_shipping: 'Envio', cart_shipping_included: 'Incluído', cart_currency: 'COP',
      cart_total: 'TOTAL', cart_discount: 'Desconto',
      nav_cart: 'Carrinho', fab_text: 'VER MEU PEDIDO',
      pay_nequi_btn: 'IR PAGAR COM NEQUI',
      pay_qr_title: 'Escaneie para pagar com Nequi', pay_qr_placeholder: 'QR DE PAGAMENTO', pay_qr_hint: 'Abra o Nequi e escaneie o código',
      pay_cancel: 'Cancelar e continuar comprando',
      pay_nequi_account: 'Conta Nequi:',
      pay_creating: 'Gerando seu pedido...', pay_error: 'Erro ao criar o pedido', pay_error_qr: 'Não foi possível gerar o pagamento', pay_error_final: 'Erro no pagamento',
      pay_step_order: 'Seu pedido', pay_step_scan: 'Escaneie', pay_step_done: 'Confirmação',
      pay_waiting: 'Aguardando confirmação do pagamento...', pay_timeout: 'O tempo de espera esgotou',
      pay_paid: 'Pagamento confirmado', pay_rejected: 'Pagamento rejeitado', pay_expired: 'Pagamento expirado, tente novamente',
      pay_success: 'Pagamento confirmado!', pay_success_text: 'Obrigado por comprar na IO QUE Artesanías.',
      pay_order_label: 'Pedido',
      pay_mp_text: 'Escolha seu método de pagamento.', pay_mp_btn: 'Pagar',
      pay_secure: 'Pagamento seguro',
      footer_desc: 'Artesanato em couro. Feito à mão desde a Colômbia.',
      footer_nav: 'Navegação', footer_inicio: 'Início',
      footer_redes: 'Redes', footer_contacto: 'Contato', footer_pagos: 'Pagamentos',
      footer_copy: '&copy; 2026 IOQUE · Feito à mão',
      footer_terminos: 'Termos', footer_privacidade: 'Privacidade', footer_envios: 'Envios'
    },
    fr: {
      nav_esencia: 'Essence', nav_catalogo: 'Catalogue', nav_historias: 'Histoires', nav_contacto: 'Contact',
      theme_toggle: 'Thème',
      hero_badge: 'Édition Limitée · Fait à la Main', hero_subtitle: 'Artesanias',
      hero_tagline: '"Le lien qui nous unit"',
      hero_text: 'Cuir · Fil · Aiguille · Chaque porte-clés est une pièce unique d\'art portable.',
      hero_explorar: 'Explorer', hero_historias_btn: 'Histoires',
      social_instagram: 'Instagram', social_tiktok: 'TikTok', social_youtube: 'YouTube', social_facebook: 'Facebook',
      esencia_label: '// 001', esencia_title: 'La <span style="color:var(--accent);">matière</span> de l\'art',
      esencia_desc: 'Il n\'y a pas deux pièces identiques. Chaque porte-clés est le résultat d\'un dialogue entre la main et la matière.',
      esencia_valor1_title: 'Cuir', esencia_valor1_text: 'Sélectionné, coupé, travaillé. Chaque pièce raconte sa propre histoire avant de devenir un porte-clés.',
      esencia_valor2_title: 'Fil', esencia_valor2_text: 'Ciré, résistant. Chaque point est délibéré, comme chaque mot dans une lettre écrite à la main.',
      esencia_valor3_title: 'Âme', esencia_valor3_text: 'Chaque race a un esprit. Nous capturons ce geste, ce regard, cette énergie inimitable.',
      proceso_cortar: 'Couper', proceso_coser: 'Coudre', proceso_montar: 'Assembler', proceso_empacar: 'Emballer',
      catalogo_label: '// 002', catalogo_title: 'Galerie <span style="color:var(--accent);">Animaux</span>',
      catalogo_desc: 'Une collection de portraits en cuir. Chacun avec sa propre fréquence.',
      anadir: 'Ajouter',
      historias_label: '// 003', historias_title: 'Légendes <span style="color:var(--accent);">à pattes</span>',
      historias_desc: 'Des chiens qui ont changé le monde. Chacun à sa manière.',
      cart_title: 'Mon Panier', cart_empty: 'Vide', cart_empty_sub: 'Ajoutez des produits du catalogue',
      cart_subtotal: 'Sous-total', cart_shipping: 'Livraison', cart_shipping_included: 'Incluse', cart_currency: 'COP',
      cart_total: 'TOTAL', cart_discount: 'Remise',
      nav_cart: 'Panier', fab_text: 'VOIR MA COMMANDE',
      pay_nequi_btn: 'PAYER AVEC NEQUI',
      pay_qr_title: 'Scannez pour payer avec Nequi', pay_qr_placeholder: 'QR DE PAIEMENT', pay_qr_hint: 'Ouvrez Nequi et scannez le code',
      pay_cancel: 'Annuler et continuer les achats',
      pay_nequi_account: 'Compte Nequi :',
      pay_creating: 'Génération de votre commande...', pay_error: 'Erreur lors de la création de la commande', pay_error_qr: 'Impossible de générer le paiement', pay_error_final: 'Erreur de paiement',
      pay_step_order: 'Votre commande', pay_step_scan: 'Scannez', pay_step_done: 'Confirmation',
      pay_waiting: 'En attente de confirmation du paiement...', pay_timeout: 'Le délai d\'attente est dépassé',
      pay_paid: 'Paiement confirmé', pay_rejected: 'Paiement refusé', pay_expired: 'Paiement expiré, réessayez',
      pay_success: 'Paiement confirmé !', pay_success_text: 'Merci d\'avoir acheté chez IO QUE Artesanías.',
      pay_order_label: 'Commande',
      pay_mp_text: 'Choisissez votre méthode de paiement.', pay_mp_btn: 'Payer',
      pay_secure: 'Paiement sécurisé',
      footer_desc: 'Artisanat du cuir. Fait à la main depuis la Colombie.',
      footer_nav: 'Navigation', footer_inicio: 'Accueil',
      footer_redes: 'Réseaux', footer_contacto: 'Contact', footer_pagos: 'Paiements',
      footer_copy: '&copy; 2026 IOQUE · Fait à la main',
      footer_terminos: 'Conditions', footer_privacidad: 'Confidentialité', footer_envios: 'Livraison'
    }
  };

  let currentLang = localStorage.getItem('ioque-lang') || 'es';
  let subtitleBuilt = false;

  const categoryIcons = {
    'Mascotas': 'fa-solid fa-paw',
    'Pets': 'fa-solid fa-paw',
    'Animais de Estimação': 'fa-solid fa-paw',
    'Animaux': 'fa-solid fa-paw',
    'Perros': 'fa-solid fa-dog',
    'Dogs': 'fa-solid fa-dog',
    'Cães': 'fa-solid fa-dog',
    'Chiens': 'fa-solid fa-dog',
    'Cuyes': 'fa-solid fa-hippo',
    'Guinea Pigs': 'fa-solid fa-hippo',
    'Porquinhos-da-índia': 'fa-solid fa-hippo',
    'Cobayes': 'fa-solid fa-hippo',
    'Religión': 'fa-solid fa-cross',
    'Religion': 'fa-solid fa-cross',
    'Religião': 'fa-solid fa-cross',
    'Personalizados': 'fa-solid fa-pen-nib',
    'Custom': 'fa-solid fa-pen-nib',
    'Personnalisés': 'fa-solid fa-pen-nib'
  };

  function getCategoryIcon(name) {
    return categoryIcons[name] || 'fa-solid fa-tag';
  }

  async function loadCategories() {
    try {
      var res = await fetch('/api/categories/?language=' + currentLang);
      var json = await res.json();
      var cats = json.results || json;
      var desktop = document.getElementById('nav-catalogo-desktop');
      var mobile = document.getElementById('nav-catalogo-mobile');
      if (!desktop || !mobile) return;
      var html = '';
      cats.forEach(function(c) {
        if (!c.active) return;
        var icon = getCategoryIcon(c.name);
        html += '<a href="#catalogo" onclick="closeMobileMenu()"><i class="' + icon + '"></i> ' + c.name + '</a>';
      });
      desktop.innerHTML = html;
      var mobHtml = '';
      cats.forEach(function(c) {
        if (!c.active) return;
        var icon = getCategoryIcon(c.name);
        mobHtml += '<a href="#catalogo" onclick="event.stopPropagation();closeMobileMenu()"><i class="' + icon + '"></i> ' + c.name + '</a>';
      });
      mobile.innerHTML = mobHtml;
      var mascotCat = cats.find(function(c) { return c.id === 1; });
      if (mascotCat) {
        var titleEl = document.querySelector('[data-i18n="catalogo_title"]');
        if (titleEl) titleEl.innerHTML = 'Galería <span style="color:var(--accent);">' + mascotCat.name + '</span>';
      }
    } catch (e) {
      console.error('[IOQUE] Error loading categories:', e);
    }
  }

  function rebuildSubtitle(text) {
    const container = document.querySelector('.hero-subtitle');
    if (!container) return;
    const baseDelay = subtitleBuilt ? 0.1 : 2.7;
    const stagger = subtitleBuilt ? 0.05 : 0.08;
    container.innerHTML = '';
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      const span = document.createElement('span');
      span.style.setProperty('--i', i);
      span.style.animationDelay = `calc(${baseDelay}s + (var(--i) * ${stagger}s))`;
      if (ch === ' ') {
        span.className = 'hero-subtitle-space';
        span.innerHTML = '&nbsp;';
      } else {
        span.textContent = ch;
      }
      container.appendChild(span);
    }
    subtitleBuilt = true;
  }

  function applyLang(lang) {
    const t = translations[lang];
    if (!t) return;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (t[key] !== undefined) {
        if (key === 'hero_subtitle') {
          rebuildSubtitle(t[key]);
        } else if (key === 'hero_tagline' || key === 'esencia_title' || key === 'catalogo_title' || key === 'historias_title') {
          el.innerHTML = t[key];
        } else {
          el.textContent = t[key];
        }
      }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (t[key] !== undefined) el.placeholder = t[key];
    });

    var selNav = document.getElementById('lang-select-nav');
    var selMob = document.getElementById('lang-select-mob');
    if (selNav) selNav.value = lang;
    if (selMob) selMob.value = lang;

    currentLang = lang;
    localStorage.setItem('ioque-lang', lang);
    loadAllCategories();
    loadCategories();
  }

  function changeLang(lang) {
    applyLang(lang);
  }

  /* ── Theme ── */
  let currentTheme = localStorage.getItem('ioque-theme') || 'dark';

  function applyTheme(theme) {
    const html = document.documentElement;
    const icon = document.getElementById('theme-icon');
    const iconMob = document.getElementById('theme-icon-mob');
    if (theme === 'warm') {
      html.classList.add('theme-warm');
      if (icon) icon.className = 'fa-solid fa-moon';
      if (iconMob) iconMob.className = 'fa-solid fa-moon';
    } else {
      html.classList.remove('theme-warm');
      if (icon) icon.className = 'fa-solid fa-sun';
      if (iconMob) iconMob.className = 'fa-solid fa-sun';
    }
    currentTheme = theme;
    localStorage.setItem('ioque-theme', theme);
  }

  function toggleTheme() {
    applyTheme(currentTheme === 'dark' ? 'warm' : 'dark');
  }

  applyTheme(currentTheme);
  applyLang(currentLang);


  /* ── WhatsApp Widget (Web Component) ── */
