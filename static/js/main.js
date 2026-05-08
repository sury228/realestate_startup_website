/* === Mahamaya Real Estate — Main JavaScript === */

window.addEventListener('load', function () {
  const loader = document.querySelector('.page-loader');
  if (!loader) return;

  if (sessionStorage.getItem('splashShown')) {
    loader.classList.add('hidden');
    return;
  }

  setTimeout(() => {
    loader.classList.add('hidden');
    sessionStorage.setItem('splashShown', 'true');
  }, 1900);
});

document.addEventListener('DOMContentLoaded', function () {
  document.body.classList.add('page-loaded');

  // Smooth page navigation
  document.querySelectorAll('a[href]:not([target="_blank"]):not([href^="#"])').forEach(link => {
    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin) return;

    link.addEventListener('click', function (event) {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (url.href === window.location.href) return;
      event.preventDefault();
      document.body.classList.remove('page-loaded');
      document.body.classList.add('page-transition');
      setTimeout(() => {
        window.location.href = url.href;
      }, 260);
    });
  });

  // Navbar scroll effect
  const navbar = document.querySelector('.navbar-custom');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
  }

  // Scroll reveal animation
  const revealElements = document.querySelectorAll('.reveal');
  const revealOnScroll = () => {
    revealElements.forEach(el => {
      const windowHeight = window.innerHeight;
      const revealTop = el.getBoundingClientRect().top;
      if (revealTop < windowHeight - 80) {
        el.classList.add('active');
      }
    });
  };
  window.addEventListener('scroll', revealOnScroll);
  revealOnScroll();

  // Auto-dismiss flash messages
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach(msg => {
    setTimeout(() => {
      msg.style.animation = 'slideOutRight 0.4s ease forwards';
      setTimeout(() => msg.remove(), 400);
    }, 5000);
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Image preview for file uploads (admin)
  const imageInput = document.getElementById('image-upload');
  const imagePreview = document.getElementById('image-preview');
  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          imagePreview.src = e.target.result;
          imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Contact form validation
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      const name = document.getElementById('name');
      const email = document.getElementById('email');
      const message = document.getElementById('message');
      let valid = true;

      [name, email, message].forEach(field => {
        if (field && !field.value.trim()) {
          field.classList.add('is-invalid');
          valid = false;
        } else if (field) {
          field.classList.remove('is-invalid');
        }
      });

      if (email && email.value && !validateEmail(email.value)) {
        email.classList.add('is-invalid');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
      }
    });
  }

  // Search form auto-submit on filter change
  const filterSelects = document.querySelectorAll('.filter-auto-submit');
  filterSelects.forEach(select => {
    select.addEventListener('change', function () {
      this.closest('form').submit();
    });
  });

  // Delete confirmation
  document.querySelectorAll('.btn-delete-confirm').forEach(btn => {
    btn.addEventListener('click', function (e) {
      if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Counter animation for stats
  const counters = document.querySelectorAll('.counter-animate');
  const animateCounter = (el) => {
    const target = parseInt(el.getAttribute('data-target'));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target + '+';
        clearInterval(timer);
      } else {
        el.textContent = Math.floor(current) + '+';
      }
    }, 16);
  };

  const observerOptions = { threshold: 0.5 };
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);

  counters.forEach(counter => counterObserver.observe(counter));

  // Mobile admin sidebar toggle
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.admin-sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }
});

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Add slideOutRight animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes slideOutRight {
    to { transform: translateX(120%); opacity: 0; }
  }
  .admin-sidebar.show { display: block !important; position: fixed; }
`;
document.head.appendChild(styleSheet);
