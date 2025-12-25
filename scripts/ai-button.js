// AI Assistant floating button - adds to all pages
(function() {
  function isRfePage() {
    const path = window.location.pathname;
    const href = window.location.href;
    return path.includes('rfe-data') ||
           path.includes('rfe-statistics') ||
           href.includes('rfe-data') ||
           href.includes('rfe-statistics');
  }

  function updateButtonPosition() {
    const btn = document.getElementById('ai-assistant-btn');
    if (!btn) return;
    btn.style.bottom = isRfePage() ? '90px' : '5px';
  }

  function createButton() {
    // Don't add if already exists
    if (document.getElementById('ai-assistant-btn')) return;

    // Create button element
    const btn = document.createElement('a');
    btn.id = 'ai-assistant-btn';
    btn.href = 'https://t.me/usa140Bot';
    btn.target = '_blank';
    btn.rel = 'noopener noreferrer';

    btn.innerHTML = `
      <div style="width: 12px; height: 12px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 14px #22c55e; animation: aiPulse 1.5s ease-in-out infinite;"></div>
      <div>
        <div style="font-size: 15px; font-weight: 700; color: white;">AI-помощник по EB-1</div>
        <div style="font-size: 11px; color: #94a3b8;">бесплатно • онлайн</div>
      </div>
    `;

    // Apply styles
    btn.style.cssText = `
      position: fixed;
      bottom: 5px;
      right: 24px;
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 16px 24px;
      background: #0f172a;
      border-radius: 16px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.25);
      text-decoration: none;
      transition: transform 0.2s ease, box-shadow 0.2s ease, bottom 0.3s ease;
    `;

    // Hover effects
    btn.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
      this.style.boxShadow = '0 12px 40px rgba(0,0,0,0.35)';
    });

    btn.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 8px 30px rgba(0,0,0,0.25)';
    });

    // Add pulse animation styles
    const style = document.createElement('style');
    style.textContent = `
      @keyframes aiPulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
      }

      @media (max-width: 600px) {
        #ai-assistant-btn {
          padding: 12px 16px !important;
          right: 16px !important;
          gap: 10px !important;
        }
        #ai-assistant-btn > div:last-child > div:first-child {
          font-size: 13px !important;
        }
        #ai-assistant-btn > div:last-child > div:last-child {
          font-size: 10px !important;
        }
      }
    `;
    document.head.appendChild(style);

    // Add button to page
    document.body.appendChild(btn);
  }

  // Create button
  createButton();

  // Update position initially and on URL changes
  updateButtonPosition();

  // Check URL periodically for client-side navigation
  setInterval(updateButtonPosition, 500);
})();
