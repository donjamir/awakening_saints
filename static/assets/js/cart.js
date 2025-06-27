
        function cartHandler() {
            return {
                activeTab: "cart",
                loading: false,
                shippingOption: "4.99",
                discount: 27.00,
                cart: [
                    {
                        name: "Lorem",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 89.99,
                        qty: 1,
                        color: "Black",
                        size: "M"
                    },
                    {
                        name: "Character",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 64.99,
                        discount: 10.96,
                        qty: 2,
                        color: "White",
                        size: "L"
                    },
                    {
                        name: "Sed do",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 49.99,
                        qty: 1,
                        color: "Blue",
                        size: "S"
                    },
                    {
                        name: "Lorem ",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 89.99,
                        qty: 1,
                        color: "Black",
                        size: "M"
                    },
                    {
                        name: "Character",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 64.99,
                        discount: 10.96,
                        qty: 2,
                        color: "White",
                        size: "L"
                    },
                    {
                        name: "Character",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 64.99,
                        discount: 10.96,
                        qty: 2,
                        color: "White",
                        size: "L"
                    },
                    {
                        name: "Sed do",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 49.99,
                        qty: 1,
                        color: "Blue",
                        size: "S"
                    },
                    {
                        name: "Lorem ",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 89.99,
                        qty: 1,
                        color: "Black",
                        size: "M"
                    },
                    {
                        name: "Character",
                        image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
                        price: 64.99,
                        discount: 10.96,
                        qty: 2,
                        color: "White",
                        size: "L"
                    },
                ],

                get subtotal() {
                    return this.cart.reduce((sum, item) => sum + item.price * item.qty, 0);
                },
                
                get grandTotal() {
                    return this.subtotal + parseFloat(this.shippingOption) - this.discount;
                },
                
                updateTotal() {
                    // Reactive update handled automatically by Alpine.js
                },
                
                removeItem(index) {
                    this.cart.splice(index, 1);
                },
                
                goToCheckout() {
                    this.loading = true;
                    setTimeout(() => {
                        this.activeTab = "checkout";
                        this.loading = false;
                    }, 600);
                },
                
                goBackToCart() {
                    this.loading = true;
                    setTimeout(() => {
                        this.activeTab = "cart";
                        this.loading = false;
                    }, 600);
                },
                
                continueShopping() {
                    // In a real app, this would redirect to the products page
                    alert("Continue shopping functionality would go here");
                }
            };
        }

        // Initialize fade-in animations
        document.addEventListener('DOMContentLoaded', function() {
            const fadeElements = document.querySelectorAll('.fade-in');
            fadeElements.forEach((el, index) => {
                el.style.animationDelay = `${index * 0.1}s`;
            });
        });