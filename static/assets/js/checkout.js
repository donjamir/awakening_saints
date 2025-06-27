
function checkoutForm() {
    return {
        form: {
            fullName: '',
            email: '',
            address: '',
            city: '',
            zip: '',
            paymentMethod: '',
            cardNumber: '',
            expiry: '',
            cvv: '',
            paypalEmail: '',
            mobileNumber: '',
            accountName: '',
            accountNumber: ''
        },
        errors: {},

        init() {
          // Add event listener for custom submission trigger
            this.$el.addEventListener('trigger-submit', () => {
                this.submitOrder();
              })
        },


        validateForm() {
            this.errors = {};  // Reset errors

            // Basic validations
            if (!this.form.fullName) this.errors.fullName = true;
            if (!this.form.email || !this.form.email.includes('@')) this.errors.email = true;
            if (!this.form.address) this.errors.address = true;
            if (!this.form.city) this.errors.city = true;
            if (!this.form.zip) this.errors.zip = true;
            if (!this.form.paymentMethod) this.errors.paymentMethod = true;

            // Conditional payment validations
            if (this.form.paymentMethod === 'credit') {
                if (!this.form.cardNumber) this.errors.cardNumber = true;
                if (!this.form.expiry) this.errors.expiry = true;
                if (!this.form.cvv) this.errors.cvv = true;
            } else if (this.form.paymentMethod === 'paypal') {
                if (!this.form.paypalEmail || !this.form.paypalEmail.includes('@')) this.errors.paypalEmail = true;
            } else if (this.form.paymentMethod === 'mobile') {
                if (!this.form.mobileNumber) this.errors.mobileNumber = true;
            } else if (this.form.paymentMethod === 'bank') {
                if (!this.form.accountName) this.errors.accountName = true;
                if (!this.form.accountNumber) this.errors.accountNumber = true;
            }

            return Object.keys(this.errors).length === 0;
        },

        async submitOrder() {
            if (!this.validateForm()) {
                // Errors exist
                return;
            }

            try {
                const response = await fetch('/your-checkout-endpoint/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')  // Ensure CSRF token is handled
                    },
                    body: JSON.stringify(this.form)
                });

                if (response.ok) {
                    alert('Order placed successfully!');
                    // Optionally redirect or reset form
                } else {
                    alert('Something went wrong. Please try again.');
                }
            } catch (error) {
                console.error('Error submitting form:', error);
                alert('Submission failed.');
            }
        }
    };
}

// Helper function to get CSRF token (Django-specific)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if cookie starts with name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
