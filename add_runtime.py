#!/usr/bin/env python
# -*- coding: utf-8 -*-

runtime_code = '''
    document.addEventListener('DOMContentLoaded', function() {
      // Renderizar CTA Final
      const ctaButtonsGrid = document.getElementById('ctaButtonsGrid');
      if (ctaButtonsGrid && typeof STORES !== 'undefined') {
        STORES.forEach(store => {
          const buttonDiv = document.createElement('div');
          buttonDiv.className = `cta-button-item ${store.isBoutique ? 'boutique' : ''}`;
          
          if (store.isBoutique) {
            buttonDiv.innerHTML = `
              <button class="cta-btn cta-btn-disabled" disabled>
                Acesso sob convite
              </button>
            `;
          } else {
            buttonDiv.innerHTML = `
              <a href="${store.loginUrl}" target="_blank" rel="noopener noreferrer" class="cta-btn cta-btn-primary">
                Entrar em ${store.nome}
              </a>
            `;
          }
          
          ctaButtonsGrid.appendChild(buttonDiv);
        });
      }

      // Meta Pixel Lead event - dispara quando usuário clica nos botões CTA das lojas
      const ctaButtons = document.querySelectorAll('.loja-card-cta-primary, .cta-btn-primary');
      ctaButtons.forEach(function(button) {
        button.addEventListener('click', function() {
          if (typeof fbq !== 'undefined') {
            fbq('track', 'Lead');
          }
        });
      });
    });'''

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the simple DOMContentLoaded code with the new one
old_code = """    document.addEventListener('DOMContentLoaded', function() {
      // Meta Pixel Lead event - dispara quando usuário clica nos botões CTA das lojas
      const ctaButtons = document.querySelectorAll('.loja-card-cta-primary');
      ctaButtons.forEach(function(button) {
        button.addEventListener('click', function() {
          if (typeof fbq !== 'undefined') {
            fbq('track', 'Lead');
          }
        });
      });
    });"""

if old_code in content:
    new_content = content.replace(old_code, runtime_code)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("DOMContentLoaded code updated successfully!")
else:
    print("Could not find the DOMContentLoaded code to replace")
