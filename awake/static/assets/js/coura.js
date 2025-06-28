
function productCarousel() {
  return {
    currentIndex: 0,
    productsPerView: 5,
    products: [
      { name: 'Denim Jacket', price: '119.00', image1: 'https://randomuser.me/api/portraits/women/44.jpg', image2: 'https://randomuser.me/api/portraits/women/45.jpg' },
      { name: 'Running Shoes', price: '89.99', image1: 'https://randomuser.me/api/portraits/men/22.jpg', image2: 'https://randomuser.me/api/portraits/men/23.jpg' },
      { name: 'Backpack', price: '64.50', image1: 'https://randomuser.me/api/portraits/men/22.jpg', image2: 'https://randomuser.me/api/portraits/men/23.jpg' },
      { name: 'Casual Shirt', price: '45.00', image1: 'https://randomuser.me/api/portraits/men/33.jpg', image2: 'https://randomuser.me/api/portraits/men/34.jpg' },
      { name: 'Sneakers', price: '99.00', image1: 'https://randomuser.me/api/portraits/women/12.jpg', image2: 'https://randomuser.me/api/portraits/women/13.jpg' },
      { name: 'Winter Coat', price: '180.00', image1: 'https://randomuser.me/api/portraits/women/50.jpg', image2: 'https://randomuser.me/api/portraits/women/51.jpg' },
      { name: 'T-shirt', price: '25.00', image1: 'https://randomuser.me/api/portraits/men/20.jpg', image2: 'https://randomuser.me/api/portraits/men/21.jpg' },
      { name: 'Jeans', price: '70.00', image1: 'https://randomuser.me/api/portraits/men/30.jpg', image2: 'https://randomuser.me/api/portraits/men/31.jpg' },
      { name: 'Cap', price: '15.00', image1: 'https://randomuser.me/api/portraits/men/40.jpg', image2: 'https://randomuser.me/api/portraits/men/41.jpg' }
    ],

    get maxIndex() {
      return this.products.length - this.productsPerView;
    },

    updateResponsiveView() {
      const w = window.innerWidth;
      if (w <= 480) this.productsPerView = 1;
      else if (w <= 768) this.productsPerView = 2;
      else if (w <= 992) this.productsPerView = 3;
      else this.productsPerView = 5;

      // Clamp currentIndex if out of range
      if (this.currentIndex > this.maxIndex) this.currentIndex = this.maxIndex < 0 ? 0 : this.maxIndex;
    },

    next() {
      if (this.currentIndex < this.maxIndex) this.currentIndex++;
    },

    prev() {
      if (this.currentIndex > 0) this.currentIndex--;
    },

    goTo(index) {
      this.currentIndex = Math.min(index, this.maxIndex);
    },

    // Touch/swipe vars
    // touchStartX: 0,
    // touchEndX: 0,
    // minSwipeDistance: 50,

    // touchStart(event) {
    //   this.touchStartX = event.touches[0].clientX;
    // },

    // touchMove(event) {
    //   this.touchEndX = event.touches[0].clientX;
    // },

    // touchEnd() {
    //   const distance = this.touchEndX - this.touchStartX;
    //   if (Math.abs(distance) > this.minSwipeDistance) {
    //     if (distance < 0) this.next();    // swipe left => next
    //     else this.prev();                 // swipe right => prev
    //   }
    //   this.touchStartX = 0;
    //   this.touchEndX = 0;
    // },

    initSwipe() {
      this.updateResponsiveView();
      window.addEventListener('resize', () => {
        this.updateResponsiveView();
      });
    }
  }
}
