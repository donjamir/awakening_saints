
        function accountDashboard() {
            return {
                activeTab: 'orders',
                orderSearch: '',
                selectedOrder: null,
                loading: false,
                setTab(tab) {
                    this.loading = true;
                    setTimeout(() => {
                        this.activeTab = tab;
                        this.loading = false;
                    }, 600);},
                orders: [
                    {
                        id: '#ORD-2024-1278',
                        status: 'Processing',
                        goods: 3,
                        total: '$784.99',
                        date: 'Feb 15, 2025',
                        items: [
                            { name: 'Wireless Headphones', quantity: 1, price: '$299.99' },
                            { name: 'Smart Watch', quantity: 1, price: '$349.99' },
                            { name: 'Charging Cable', quantity: 2, price: '$19.99' }
                        ]
                    },
                    {
                        id: '#ORD-2024-1265',
                        status: 'Skipped',
                        goods: 2,
                        total: '$459.99',
                        date: 'Feb 10, 2025',
                        items: [
                            { name: 'Laptop Sleeve', quantity: 1, price: '$39.99' },
                            { name: 'Wireless Mouse', quantity: 1, price: '$59.99' }
                    ]
                    },
                    {
                        id: '#ORD-2024-1259',
                        status: 'Delivered',
                        goods: 1,
                        total: '$129.99',
                        date: 'Feb 5, 2025',
                        items: [
                            { name: 'Bluetooth Speaker', quantity: 1, price: '$129.99' }
                        ]
                    },
                    {
                        id: '#ORD-2024-1243',
                        status: 'Cancelled',
                        goods: 3,
                        total: '$1,049.99',
                        date: 'Jan 28, 2025',
                        items: [
                            { name: 'Gaming Console', quantity: 1, price: '$499.99' },
                            { name: 'Controller', quantity: 2, price: '$59.99' },
                            { name: 'Game Bundle', quantity: 1, price: '$89.99' }
                        ]
                    }
                
                ],
                 get filteredOrders() {
                    if (!this.orderSearch) return this.orders;
                    
                    const searchTerm = this.orderSearch.toLowerCase();
                    return this.orders.filter(order => 
                        order.id.toLowerCase().includes(searchTerm) ||
                        order.status.toLowerCase().includes(searchTerm) ||
                        order.total.toLowerCase().includes(searchTerm) ||
                        order.date.toLowerCase().includes(searchTerm)
                    );
                },
                calculateSubtotal(items) {
                    if (!items) return '$0.00';
                    
                    let subtotal = 0;
                    for (let item of items) {
                        const price = parseFloat(item.price.replace(/[^0-9.-]+/g,""));
                        subtotal += price * item.quantity;
                    }
                    return `$${subtotal.toFixed(2)}`;
                },

                wishlist: [
                    {
                        name: 'Wireless Bluetooth Headphones',
                        price: '$129.99',
                        image: 'headphones'
                    },
                    {
                        name: 'Smart Watch Series 5',
                        price: '$299.99',
                        image: 'smartwatch'
                    },
                    {
                        name: 'Premium Leather B',
                        price: '$89.99',
                        image: 'backpack'
                    }, 
                    {
                        name: 'Watch  5',
                        price: '$299.99',
                        image: 'smartwatch'
                    },
                    {
                        name: 'Leather pack',
                        price: '$89.99',
                        image: 'backpack'
                    }
                ],
                paymentMethods: [
                    {
                        type: 'Credit Card',
                        last4: '**** 4242',
                        name: 'Visa',
                        icon: 'credit-card'
                    },
                    {
                        type: 'PayPal',
                        email: 'anderson@example.com',
                        icon: 'paypal'
                    },
                    {
                        type: 'Apple Pay',
                        phone: '•••• •••• •••• 1234',
                        icon: 'apple'
                    }
                ],
                addresses: [
                    {
                        name: 'Home',
                        address: '123 Main Street, Apt 4B, New York, NY 10001, United States',
                        primary: true
                    },
                    {
                        name: 'Office',
                        address: '456 Business Ave, Floor 12, New York, NY 10005, United States',
                        primary: false
                    }
                ],
                helpTopics: [
                    {
                        title: 'How to track my order?',
                        content: 'You can track your order from the "My Orders" section. Click on "View Details" for your order to see tracking information.'
                    },
                    {
                        title: 'What is your return policy?',
                        content: 'We accept returns within 30 days of purchase. Items must be in original condition with tags attached.'
                    },
                    {
                        title: 'How do I change my password?',
                        content: 'You can change your password from the "Account Settings" section under the "Security" tab.'
                    }
                ]
            }
        }