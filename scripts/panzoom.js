(function() {
  // Wait for DOM to be ready
  function initPanZoom() {
    const container = document.getElementById('panzoom-container');
    const content = document.getElementById('panzoom-content');
    if (!container || !content) {
      // Retry after a short delay if elements not found
      setTimeout(initPanZoom, 500);
      return;
    }

    let scale = 0.4;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let startX, startY;

    function updateTransform() {
      content.style.transform = 'translate(' + translateX + 'px, ' + translateY + 'px) scale(' + scale + ')';
    }

    updateTransform();

    container.addEventListener('wheel', function(e) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      scale = Math.min(Math.max(0.1, scale * delta), 3);
      updateTransform();
    }, { passive: false });

    container.addEventListener('mousedown', function(e) {
      isDragging = true;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
      container.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      updateTransform();
    });

    document.addEventListener('mouseup', function() {
      isDragging = false;
      if (container) container.style.cursor = 'grab';
    });

    const zoomIn = document.getElementById('zoom-in');
    const zoomOut = document.getElementById('zoom-out');
    const reset = document.getElementById('reset');

    if (zoomIn) {
      zoomIn.addEventListener('click', function() {
        scale = Math.min(scale * 1.2, 3);
        updateTransform();
      });
    }

    if (zoomOut) {
      zoomOut.addEventListener('click', function() {
        scale = Math.max(scale * 0.8, 0.1);
        updateTransform();
      });
    }

    if (reset) {
      reset.addEventListener('click', function() {
        scale = 0.4;
        translateX = 0;
        translateY = 0;
        updateTransform();
      });
    }

    console.log('PanZoom initialized');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanZoom);
  } else {
    initPanZoom();
  }
})();
