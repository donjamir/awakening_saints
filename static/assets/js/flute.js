document.getElementById("payNowButton").addEventListener("click", function () {
    // Collect form data
    const donorName = document.getElementById("donor_name").value;
    const donorEmail = document.getElementById("donor_email").value;
    const phone = document.getElementById("phone").value;
    const amount = document.getElementById("donation_amount").value;
    const currency = document.getElementById("currency").value;
    const message = document.getElementById("donation_message").value;

    // Flutterwave Payment Configuration
    FlutterwaveCheckout({
        public_key: "FLWPUBK-4428954ab2b6a3921e716331f673338e-X", // Replace with your Flutterwave public key
        tx_ref: "donation_" + Date.now(),
        amount: amount,
        currency: currency,
        customer: {
            email: donorEmail,
            phone_number: phone,
            name: donorName,
        },
        customizations: {
            //title: "Charity Donation",
           // description: message,
            logo: "https://awakeningsaints.org/index.php", // Replace with your organization's logo URL
        },
        callback: function (data) {
            console.log(data);
            alert("Payment successful! Transaction ID: " + data.transaction_id);
        },
        onclose: function () {
            alert("Transaction closed.");
        },
    });
});