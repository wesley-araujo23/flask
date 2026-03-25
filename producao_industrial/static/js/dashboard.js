// ==========================================================================
// DASHBOARD.JS - ULTRA PREMIUM EFFECTS
// ==========================================================================

class DashboardPremium {
    constructor() {
        this.init();
        this.bindEvents();
        this.startAnimations();
        this.setupParticles();
        this.setupStatsAnimation();
        this.setupThemeSwitcher();
        this.setupSearch();
    }

    init() {
        // Previne FOUC (Flash of Unstyled Content)
        document.body.classList.add('loaded');
        
        // Detecta preferências do usuário
        this.setupReducedMotion();
        this.setupTheme();
    }

    bindEvents() {
        // Mobile menu
        const mobileBtn = document.querySelector('.mobile-menu-btn');
        const mainNav = document.querySelector('.main-nav');
        
        if (mobileBtn && mainNav) {
            mobileBtn.addEventListener('click', () => {
                mainNav.classList.toggle('active');
                document.body.classList.toggle('menu-open');
            });
        }

        // Close mobile menu on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.main-header') && !e.target.closest('.main-nav')) {
                mainNav?.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });

        // Auto-hide flash messages
        this.autoHideFlashMessages();

        // Navbar active link
        this.setActiveNavLink();

        // Scroll animations
        this.setupScrollAnimations();

        // Table row actions
        this.setupTableActions();

        // Form enhancements
        this.setupFormEnhancements();
    }

    // ==========================================================================
    // ANIMAÇÕES DE ENTRADA ESPECETAULARES
    // ==========================================================================
    startAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe cards, stats, tables
        document.querySelectorAll('.stat-card, .admin-stat-card, .card, .table-section, .form-card').forEach(el => {
            observer.observe(el);
        });
    }

    // ==========================================================================
    // EFEITOS DE PARTÍCULAS FLUTUANTES
    // ==========================================================================
    setupParticles() {
        const canvas = document.createElement('canvas');
        canvas.className = 'particles-canvas';
        document.querySelector('.bg-effects')?.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationId;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        function createParticle() {
            return {
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                alpha: Math.random() * 0.5 + 0.2,
                color: `hsl(${Math.random() * 60 + 160}, 70%, 60%)`
            };
        }

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(p => {
                // Update
                p.x += p.vx;
                p.y += p.vy;
                p.alpha += (Math.random() - 0.5) * 0.02;

                // Bounce edges
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

                // Draw
                ctx.save();
                ctx.globalAlpha = p.alpha;
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            });

            animationId = requestAnimationFrame(animateParticles);
        }

        resizeCanvas();
        for (let i = 0; i < 50; i++) particles.push(createParticle());
        animateParticles();

        window.addEventListener('resize', resizeCanvas);
    }

    // ==========================================================================
    // ANIMAÇÃO DE NÚMEROS CONTADORES
    // ==========================================================================
    setupStatsAnimation() {
        const stats = document.querySelectorAll('.stat-value, .stat-card span');
        
        const animateValue = (el, start, end, duration = 2000) => {
            let startTime = null;
            const step = (timestamp) => {
                if (!startTime) startTime = timestamp;
                const progress = Math.min((timestamp - startTime) / duration, 1);
                const easeProgress = 1 - Math.pow(1 - progress, 3); // easeOutCubic
                el.textContent = Math.floor(easeProgress * (end - start) + start).toLocaleString();
                
                if (progress < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const finalValue = parseInt(el.getAttribute('data-target') || el.textContent);
                    animateValue(el, 0, finalValue);
                    observer.unobserve(entry.target);
                }
            });
        });

        stats.forEach(stat => observer.observe(stat));
    }

    // ==========================================================================
    // NAVBAR ATIVA AUTOMATICAMENTE
    // ==========================================================================
    setActiveNavLink() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('section[id]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    navLinks.forEach(link => link.classList.remove('active'));
                    const id = entry.target.getAttribute('id');
                    document.querySelector(`.nav-link[href="#${id}"]`)?.classList.add('active');
                }
            });
        }, { threshold: 0.3, rootMargin: '-20% 0px -20% 0px' });

        sections.forEach(section => observer.observe(section));
    }

    // ==========================================================================
    // SCROLL ANIMATIONS SUAVES
    // ==========================================================================
    setupScrollAnimations() {
        let ticking = false;
        
        const updateScrollEffects = () => {
            const scrollY = window.scrollY;
            const orbs = document.querySelectorAll('.bg-orb');
            
            orbs.forEach((orb, index) => {
                const speed = 0.5 + index * 0.2;
                orb.style.transform = `translateY(${scrollY * speed * 0.1}px)`;
            });
            
            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollEffects);
                ticking = true;
            }
        }, { passive: true });
    }

    // ==========================================================================
    // TABELA INTERATIVA COM CHECKBOXES
    // ==========================================================================
    setupTableActions() {
        const tables = document.querySelectorAll('.data-table');
        
        tables.forEach(table => {
            const checkboxes = table.querySelectorAll('input[type="checkbox"]');
            const selectAll = table.querySelector('.select-all');
            
            if (selectAll) {
                selectAll.addEventListener('change', (e) => {
                    checkboxes.forEach(cb => cb.checked = e.target.checked);
                    this.updateTableActions(table);
                });
            }
            
            checkboxes.forEach(cb => {
                cb.addEventListener('change', () => this.updateTableActions(table));
            });
        });
    }

    updateTableActions(table) {
        const checked = table.querySelectorAll('input[type="checkbox"]:checked');
        const actionBtns = table.parentElement.querySelectorAll('.table-actions .btn');
        
        actionBtns.forEach(btn => {
            btn.style.opacity = checked.length > 0 ? '1' : '0.5';
            btn.disabled = checked.length === 0;
        });
    }

    // ==========================================================================
    // FORM ENHANCEMENTS COM VALIDAÇÃO VISUAL
    // ==========================================================================
    setupFormEnhancements() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                input.addEventListener('blur', (e) => {
                    this.validateField(e.target);
                });
                
                input.addEventListener('input', (e) => {
                    this.clearFieldError(e.target);
                });
            });
        });
    }

    validateField(input) {
        const value = input.value.trim();
        const fieldType = input.dataset.type || 'text';
        
        let isValid = true;
        let errorMsg = '';
        
        switch(fieldType) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = emailRegex.test(value);
                errorMsg = !isValid ? 'Email inválido' : '';
                break;
            case 'required':
                isValid = value.length > 0;
                errorMsg = !isValid ? 'Campo obrigatório' : '';
                break;
            case 'number':
                isValid = !isNaN(value) && value >= 0;
                errorMsg = !isValid ? 'Apenas números positivos' : '';
                break;
        }
        
        if (!isValid) {
            this.showFieldError(input, errorMsg);
        } else {
            this.clearFieldError(input);
        }
    }

    showFieldError(input, message) {
        let errorEl = input.parentElement.querySelector('.error-message');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'error-message';
            errorEl.style.cssText = `
                color: #ef4444;
                font-size: 0.75rem;
                margin-top: 0.25rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            `;
            input.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = message;
        input.classList.add('error');
    }

    clearFieldError(input) {
        const errorEl = input.parentElement.querySelector('.error-message');
        if (errorEl) errorEl.remove();
        input.classList.remove('error');
    }

    // ==========================================================================
    // FLASH MESSAGES AUTOMÁTICAS
    // ==========================================================================
    autoHideFlashMessages() {
        const flashes = document.querySelectorAll('.flash-message');
        flashes.forEach(flash => {
            setTimeout(() => {
                flash.style.animation = 'slideOutRight 0.4s ease-out forwards';
                setTimeout(() => flash.remove(), 400);
            }, 5000);
        });
    }

    // ==========================================================================
    // REDUCED MOTION DETECTION
    // ==========================================================================
    setupReducedMotion() {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        if (mediaQuery.matches) {
            document.documentElement.style.setProperty('--transition-instant', 'none');
        }
    }

    // ==========================================================================
    // THEME SWITCHER (OPCIONAL)
    // ==========================================================================
    setupThemeSwitcher() {
        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;

        toggle.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
        }
    }

    // ==========================================================================
    // BUSCA INTELIGENTE COM DEBOUNCE
    // ==========================================================================
    setupSearch() {
        const searchInput = document.getElementById('search');
        if (!searchInput) return;

        let timeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });
    }

    performSearch(query) {
        const rows = document.querySelectorAll('.data-table tbody tr');
        const noResults = document.querySelector('.no-results');

        let visibleCount = 0;
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = text.includes(query.toLowerCase());
            row.style.display = isVisible ? '' : 'none';
            
            if (isVisible) visibleCount++;
        });

        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }
}

// ==========================================================================
// INTERSECTION OBSERVER PARA EFEITOS DE SCROLL
// ==========================================================================
const scrollReveal = {
    init() {
        this.observer = new IntersectionObserver(this.reveal.bind(this), {
            threshold: 0.15,
            rootMargin: '0px 0px -10% 0px'
        });

        document.querySelectorAll('[data-reveal]').forEach(el => {
            this.observer.observe(el);
        });
    },

    reveal(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.revealDelay || 0;
                setTimeout(() => {
                    entry.target.classList.add('revealed');
                }, delay * 100);
                this.observer.unobserve(entry.target);
            }
        });
    }
};

// ==========================================================================
// INICIALIZAÇÃO AUTOMÁTICA
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    new DashboardPremium();
    scrollReveal.init();
    
    // Parallax effect para header
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const header = document.querySelector('.main-header');
        if (header) {
            header.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    }, { passive: true });
});

// ==========================================================================
// UTILITÁRIOS GLOBAIS
// ==========================================================================
window.utils = {
    // Toast notifications
    toast(message, type = 'success', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `flash-message flash-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
            <button class="flash-close">&times;</button>
        `;
        
        document.querySelector('.flash-container')?.appendChild(toast);
        
        setTimeout(() => toast.remove(), duration);
        
        toast.querySelector('.flash-close')?.addEventListener('click', () => toast.remove());
    },

    // Confirm dialog moderno
    confirm(title, message) {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay active';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem;">
                        <button class="btn btn-secondary" id="cancel">Cancelar</button>
                        <button class="btn btn-danger" id="confirm">Confirmar</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            const cancelBtn = modal.querySelector('#cancel');
            const confirmBtn = modal.querySelector('#confirm');
            const closeBtn = modal.querySelector('.modal-close');
            
            const closeModal = () => {
                modal.classList.remove('active');
                setTimeout(() => modal.remove(), 300);
            };
            
            cancelBtn.addEventListener('click', () => {
                resolve(false);
                closeModal();
            });
            
            confirmBtn.addEventListener('click', () => {
                resolve(true);
                closeModal();
            });
            
            closeBtn.addEventListener('click', closeModal);
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    resolve(false);
                    closeModal();
                }
            });
        });
    }
};

// ==========================================================================
// PROGRESS BARS ANIMADAS
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const width = entry.target.dataset.width;
                    entry.target.style.width = width;
                    observer.unobserve(entry.target);
                }
            });
        });
        observer.observe(bar);
    });
});

// Animações inputs globais
document.addEventListener('DOMContentLoaded', function() {
    // Focus icons
    document.querySelectorAll('.input-wrapper input, .search-container input').forEach(input => {
        const icon = input.parentElement.querySelector('i');
        if (icon) {
            input.addEventListener('focus', () => {
                icon.style.color = 'var(--primary)';
            });
            input.addEventListener('blur', () => {
                icon.style.color = 'var(--text-muted)';
            });
        }
    });

    // Auto-resize textarea
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Select smooth
document.addEventListener('DOMContentLoaded', function() {
    var selects = document.querySelectorAll('.input-wrapper select');
    selects.forEach(function(select) {
        select.addEventListener('focus', function() {
            this.parentElement.style.borderColor = 'var(--primary)';
        });
        select.addEventListener('blur', function() {
            this.parentElement.style.borderColor = 'rgba(255,255,255,0.15)';
        });
    });
});