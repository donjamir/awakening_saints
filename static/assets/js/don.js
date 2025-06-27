    document.getElementById("payNowButton").addEventListener("click", function (e) {
        e.preventDefault();  // Prevent default form submission

        var donorName = document.getElementById("donor_name").value;
        var donorEmail = document.getElementById("donor_email").value;
        var phone = document.getElementById("phone").value;
        var amount = document.getElementById("donation_amount").value;
        var currency = document.getElementById("currency").value;
        var donationMessage = document.getElementById("donation_message").value;

        FlutterwaveCheckout({
            public_key: "FLWPUBK-4428954ab2b6a3921e716331f673338e-X",  // Replace with your Flutterwave Public Key
            tx_ref: "TX_" + Math.floor((Math.random() * 1000000000) + 1),  // Unique transaction reference
            amount: amount,
            currency: currency,
            payment_options: "card, mobilemoney, ussd",
            customer: {
                email: donorEmail,
                phone_number: phone,
                name: donorName,
            },
            customizations: {
                title: "Charity Donation",
                description: donationMessage,
                logo: "https://yourwebsite.com/logo.png", // Replace with your logo URL
            },
            callback: function (data) {
                console.log(data);
                alert("Payment Successful! Transaction ID: " + data.transaction_id);
                // You can send the transaction_id to your server for verification
            },
            onclose: function () {
                alert("Transaction was not completed");
            },
        });
    });
