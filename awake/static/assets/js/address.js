
    document.addEventListener('alpine:init', () => {
        Alpine.store('addresses', {
            addresses: [
                { name: 'Home', address: '123 Main St, Kampala', primary: true },
                { name: 'Office', address: 'Industrial Rd, Kampala', primary: false }
            ],
            editingIndex: null,
            openAddModal() {
                this.editingIndex = null;
                Alpine.store('form').set({ name: '', address: '', primary: false });
            },
            openEditModal(index) {
                this.editingIndex = index;
                Alpine.store('form').set({ ...this.addresses[index] });
            },
            saveForm(data) {
                if (data.primary) {
                    this.addresses.forEach(addr => addr.primary = false);
                }
                if (this.editingIndex === null) {
                    this.addresses.push(data);
                } else {
                    this.addresses[this.editingIndex] = data;
                }
            },
            remove(index) {
                if (confirm('Are you sure you want to delete this address?')) {
                    const wasPrimary = this.addresses[index].primary;
                    this.addresses.splice(index, 1);
                    if (wasPrimary && this.addresses.length) {
                        this.addresses[0].primary = true;
                    }
                }
            },
            setPrimary(index) {
                this.addresses.forEach((a, i) => a.primary = i === index);
            }
        });

        Alpine.data('addressesComponent', () => ({
            get addresses() {
                return Alpine.store('addresses').addresses;
            },
            removeAddress(index) {
                Alpine.store('addresses').remove(index);
            },
            setPrimary(index) {
                Alpine.store('addresses').setPrimary(index);
            }
        }));

        Alpine.store('form', {
            form: { name: '', address: '', primary: false },
            set(data) {
                this.form = data;
            }
        });

        Alpine.data('addressForm', () => ({
            get form() {
                return Alpine.store('form').form;
            },
            errors: {},

            validate() {
                this.errors = {};
                if (!this.form.name || this.form.name.trim() === '') {
                    this.errors.name = 'Name is required.';
                }
                if (!this.form.address || this.form.address.trim() === '') {
                    this.errors.address = 'Address is required.';
                }
                return Object.keys(this.errors).length === 0;
            },

            save() {
                if (this.validate()) {
                    Alpine.store('addresses').saveForm(this.form);
                    // Optional: close modal if validation passes
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addAddressModal'));
                    if (modal) modal.hide();
                }
            },

            init() {
                this.errors = {};
            }
        }));
    });
