// Toggle credit card input fields visibility
function toggleCreditCardFields() {
    var creditCardFields = document.getElementById('creditCardFields');
    if (document.getElementById('creditCardOption').checked) {
        creditCardFields.style.display = 'block'; // Show credit card fields
    } else {
        creditCardFields.style.display = 'none'; // Hide credit card fields
    }
}

// Show custom amount input field if 'Other' amount is selected
document.getElementById('donationAmount').addEventListener('change', function () {
    var customAmountWrapper = document.getElementById('customAmountWrapper');
    if (this.value === 'custom') {
        customAmountWrapper.style.display = 'block';
    } else {
        customAmountWrapper.style.display = 'none';
    }
});
