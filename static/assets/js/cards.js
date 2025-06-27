
    document.addEventListener('alpine:init', () => {
        Alpine.store('cards', {
            cards: [
                { type: 'Visa', number: '**** **** **** 1234', expiry: '12/25', name: 'John Doe', cvv: '123', isDefault: true },
                { type: 'MasterCard', number: '**** **** **** 5678', expiry: '09/24', name: 'Jane Smith', cvv: '456', isDefault: false }
            ],
            editingIndex: null,
            openAddModal() {
                this.editingIndex = null;
                Alpine.store('cardFormStore').set({ type: 'Visa', number: '', expiry: '', cvv: '', name: '', isDefault: false });
            },
            openEditModal(index) {
                this.editingIndex = index;
                Alpine.store('cardFormStore').set({ ...this.cards[index] });
            },
            saveForm(data) {
                if (data.isDefault) {
                    this.cards.forEach(card => card.isDefault = false);
                }
                if (this.editingIndex === null) {
                    this.cards.push(data);
                } else {
                    this.cards[this.editingIndex] = data;
                }
            },
            remove(index) {
                if (confirm('Are you sure you want to delete this card?')) {
                    const wasDefault = this.cards[index].isDefault;
                    this.cards.splice(index, 1);
                    if (wasDefault && this.cards.length) {
                        this.cards[0].isDefault = true;
                    }
                }
            },
            setDefault(index) {
                this.cards.forEach((c, i) => c.isDefault = i === index);
            }
        });

        Alpine.store('cardFormStore', {
            form: { type: 'Visa', number: '', expiry: '', cvv: '', name: '', isDefault: false },
            set(data) {
                this.form = data;
            }
        });

        Alpine.data('cardForm', () => ({
            errors: {},
            get form() {
                return Alpine.store('cardFormStore').form;
            },
            validate() {
                this.errors = {};
                if (!this.form.number) this.errors.number = 'Card number is required';
                else if (!/^\d{4} \d{4} \d{4} \d{4}$/.test(this.form.number)) this.errors.number = 'Invalid format';

                if (!this.form.expiry) this.errors.expiry = 'Expiry date is required';
                else if (!/^\d{2}\/\d{2}$/.test(this.form.expiry)) this.errors.expiry = 'Use MM/YY';

                if (!this.form.cvv) this.errors.cvv = 'CVV is required';
                else if (!/^\d{3}$/.test(this.form.cvv)) this.errors.cvv = 'CVV must be 3 digits';

                if (!this.form.name) this.errors.name = 'Cardholder name is required';

                return Object.keys(this.errors).length === 0;
            },
            save() {
                if (!this.validate()) return false;
                Alpine.store('cards').saveForm(this.form);
                return true;
            },
            init() {}
        }));
    });
