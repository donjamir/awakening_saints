
  function wishlistHandler() {
    return {
      loading: false,
      wishlist: [
        {
          name: "USB-C Cable",
          image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
          price: 10.5,
          qty: 3
        },
        {
          name: "Wireless Mouse",
          image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
          price: 25.99,
          qty: 2
        },
        {
          name: "Bluetooth Headphones",
          image: "https://image.freepik.com/free-photo/black-bluetooth-headphones-on-white_1150-11452.jpg",
          price: 59.99,
          qty: 1
        },
                {
          name: "USB-C Cable",
          image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
          price: 10.5,
          qty: 3
        },
        {
          name: "Wireless Mouse",
          image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
          price: 25.99,
          qty: 2
        },
        {
          name: "Bluetooth Headphones",
          image: "https://image.freepik.com/free-photo/black-bluetooth-headphones-on-white_1150-11452.jpg",
          price: 59.99,
          qty: 1
        },
                {
          name: "USB-C Cable",
          image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
          price: 10.5,
          qty: 3
        },
        {
          name: "Wireless Mouse",
          image: "https://m.media-amazon.com/images/I/61LtuGzXeaL._AC_SL1500_.jpg",
          price: 25.99,
          qty: 2
        },
        {
          name: "Bluetooth Headphones",
          image: "https://image.freepik.com/free-photo/black-bluetooth-headphones-on-white_1150-11452.jpg",
          price: 59.99,
          qty: 1
        }
      ],
      removeItem(index) {
        this.wishlist.splice(index, 1);
      },
      addItem(item) {
        // Add item only if it doesn't exist
        if (!this.wishlist.find(i => i.name === item.name)) {
          this.wishlist.push(item);
        }
      }
    };
  }

  // Modal trigger for wishlist
  document.addEventListener("DOMContentLoaded", function () {
    const wishlistIcon = document.getElementById("wishlistIcon");
    const wishlistModal = new bootstrap.Modal(document.getElementById("wishlistModal"));
    if(wishlistIcon) {
      wishlistIcon.addEventListener("click", function (e) {
        e.preventDefault();
        wishlistModal.show();
      });
    }
  });
