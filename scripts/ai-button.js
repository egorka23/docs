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
    btn.style.bottom = isRfePage() ? '90px' : '24px';
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
      <div style="width: 14px; height: 14px; background: #a3e635; border-radius: 50%; box-shadow: 0 0 18px #a3e635, 0 0 30px #84cc16; animation: aiPulse 1.2s ease-in-out infinite;"></div>
      <div>
        <div style="font-size: 15px; font-weight: 700; color: #a3e635;">AI-помощник по EB-1</div>
        <div style="font-size: 11px; color: rgba(255,255,255,0.8); font-weight: 500;">бесплатно • онлайн</div>
      </div>
    `;

    // Apply styles with glow effect
    btn.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 16px 24px;
      background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
      border: 1px solid rgba(132, 204, 22, 0.4);
      border-radius: 16px;
      box-shadow: 0 0 30px rgba(132, 204, 22, 0.5), 0 0 60px rgba(163, 230, 53, 0.3), 0 8px 30px rgba(0,0,0,0.4);
      text-decoration: none;
      transition: transform 0.2s ease, box-shadow 0.2s ease, bottom 0.3s ease;
      animation: btnGlow 2s ease-in-out infinite, btnSlideIn 0.6s ease-out;
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

    // Add pulse and glow animation styles
    const style = document.createElement('style');
    style.textContent = `
      @keyframes aiPulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
      }

      @keyframes btnGlow {
        0%, 100% {
          box-shadow: 0 0 25px rgba(132, 204, 22, 0.5), 0 0 50px rgba(163, 230, 53, 0.3), 0 8px 30px rgba(0,0,0,0.3);
        }
        50% {
          box-shadow: 0 0 40px rgba(132, 204, 22, 0.7), 0 0 80px rgba(163, 230, 53, 0.5), 0 8px 30px rgba(0,0,0,0.3);
        }
      }

      @keyframes btnSlideIn {
        0% {
          opacity: 0;
          transform: translateY(30px) scale(0.9);
        }
        100% {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
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
