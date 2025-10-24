class AuthManager {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        // Show/hide password functionality
        this.initPasswordToggle();
        
        // Form validation
        this.initFormValidation();
        
        // Loading states
        this.initLoadingStates();
    }

    initPasswordToggle() {
        const showPasswordButtons = document.querySelectorAll('.show-password');
        
        showPasswordButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const input = button.parentElement.querySelector('input');
                const isPassword = input.type === 'password';
                
                input.type = isPassword ? 'text' : 'password';
                
                // Update icon
                const icon = button.querySelector('svg');
                if (isPassword) {
                    icon.innerHTML = '<path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z" fill="currentColor"/>';
                } else {
                    icon.innerHTML = '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/>';
                }
            });
        });
    }

    initFormValidation() {
        const forms = document.querySelectorAll('.auth-form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
            
            // Real-time validation for signup form
            if (form.id === 'signup-form') {
                this.initSignupValidation(form);
            }
        });
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        // Password confirmation validation
        const password1 = form.querySelector('input[name="password1"]');
        const password2 = form.querySelector('input[name="password2"]');
        
        if (password1 && password2 && password1.value !== password2.value) {
            this.showFieldError(password2, 'Passwords do not match');
            isValid = false;
        }
        
        return isValid;
    }

    initSignupValidation(form) {
        const passwordInput = form.querySelector('input[name="password1"]');
        const usernameInput = form.querySelector('input[name="username"]');
        const emailInput = form.querySelector('input[name="email"]');
        
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                this.validatePasswordStrength(e.target.value);
            });
        }
        
        if (usernameInput) {
            usernameInput.addEventListener('input', (e) => {
                this.validateUsername(e.target.value);
            });
        }
        
        if (emailInput) {
            emailInput.addEventListener('input', (e) => {
                this.validateEmail(e.target.value);
            });
        }
    }

    validatePasswordStrength(password) {
        let strength = 'weak';
        let message = 'Weak password';
        
        if (password.length >= 8) {
            strength = 'fair';
            message = 'Fair password';
        }
        
        if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) {
            strength = 'good';
            message = 'Good password';
        }
        
        if (password.length >= 12 && /[A-Z]/.test(password) && /[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) {
            strength = 'strong';
            message = 'Strong password';
        }
        
        this.updatePasswordStrength(strength, message);
    }

    updatePasswordStrength(strength, message) {
        let indicator = document.querySelector('.password-strength');
        
        if (!indicator) {
            const passwordInput = document.querySelector('input[name="password1"]');
            indicator = document.createElement('div');
            indicator.className = 'password-strength';
            passwordInput.parentNode.appendChild(indicator);
        }
        
        indicator.textContent = message;
        indicator.className = `password-strength strength-${strength}`;
    }

    validateUsername(username) {
        if (username.length < 3) {
            this.showFieldError(document.querySelector('input[name="username"]'), 'Username must be at least 3 characters');
        } else if (!/^[a-zA-Z0-9_.]+$/.test(username)) {
            this.showFieldError(document.querySelector('input[name="username"]'), 'Username can only contain letters, numbers, underscores, and periods');
        } else {
            this.clearFieldError(document.querySelector('input[name="username"]'));
        }
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email && !emailRegex.test(email)) {
            this.showFieldError(document.querySelector('input[name="email"]'), 'Please enter a valid email address');
        } else {
            this.clearFieldError(document.querySelector('input[name="email"]'));
        }
    }

    showFieldError(input, message) {
        this.clearFieldError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = `
            color: var(--red);
            font-size: 11px;
            margin-top: 4px;
            text-align: left;
        `;
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
        input.style.borderColor = 'var(--red)';
    }

    clearFieldError(input) {
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        input.style.borderColor = '';
    }

    initLoadingStates() {
        const forms = document.querySelectorAll('.auth-form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const button = form.querySelector('.auth-button');
                const buttonText = button.querySelector('.button-text');
                const spinner = button.querySelector('.loading-spinner');
                
                if (buttonText && spinner) {
                    buttonText.style.display = 'none';
                    spinner.style.display = 'block';
                    button.disabled = true;
                }
            });
        });
    }
}

// Initialize auth manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    new AuthManager();
});

// Auto-focus first input
document.addEventListener('DOMContentLoaded', function() {
    const firstInput = document.querySelector('.form-input');
    if (firstInput) {
        firstInput.focus();
    }
});