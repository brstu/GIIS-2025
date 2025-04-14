// Плавное появление элементов
document.addEventListener('DOMContentLoaded', () => {
  const animateOnScroll = () => {
    const elements = document.querySelectorAll('.card, .hero-section, h2');
    elements.forEach(el => {
      const elPosition = el.getBoundingClientRect().top;
      const screenPosition = window.innerHeight / 1.3;

      if(elPosition < screenPosition) {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }
    });
  };

  // Изначально прячем элементы
  document.querySelectorAll('.card, h2').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'all 0.6s ease';
  });

  window.addEventListener('scroll', animateOnScroll);
  animateOnScroll();

  // Анимация кнопок
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      btn.style.transform = 'scale(1.05)';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'scale(1)';
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  // Анимация кнопки "В корзину"
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const form = this.closest('form');

      // Анимация
      this.innerHTML = '<i class="fas fa-check"></i> Добавлено';
      this.classList.add('btn-success');
      this.classList.remove('btn-primary');

      // Встряхивающий эффект
      this.style.transform = 'translateX(10px)';
      setTimeout(() => {
        this.style.transform = 'translateX(-10px)';
        setTimeout(() => {
          this.style.transform = 'translateX(0)';
          // Отправка формы после анимации
          setTimeout(() => form.submit(), 300);
        }, 100);
      }, 100);
    });
  });

  // Параллакс эффект для героя
  const hero = document.querySelector('.parallax-bg');
  if (hero) {
    window.addEventListener('scroll', function() {
      const scroll = window.pageYOffset;
      hero.style.transform = `translateY(${scroll * 0.3}px)`;
    });
  }
});

// Анимация кнопки удаления
document.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
    });
    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });
});