document.addEventListener('DOMContentLoaded', function () {
    function toggleFields() {
        const mediaType = document.getElementById('id_media_type');
        const fileRow = document.querySelector('.form-row.field-file');
        const thumbRow = document.querySelector('.form-row.field-thumbnail');
        const textRow = document.querySelector('.form-row.field-text_body');

        if (!mediaType || !fileRow || !thumbRow || !textRow) return;

        if (mediaType.value === 'text') {
            fileRow.style.display = 'none';
            thumbRow.style.display = 'none';
            textRow.style.display = 'block';
        } else {
            fileRow.style.display = '';
            thumbRow.style.display = '';
            textRow.style.display = 'none';
        }
    }

    const mediaTypeField = document.getElementById('id_media_type');
    if (mediaTypeField) {
        toggleFields();  // On load
        mediaTypeField.addEventListener('change', toggleFields);  // On change
    }
});
