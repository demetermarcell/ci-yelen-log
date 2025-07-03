// Wait until the entire DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Get the modal element by its ID
    const createModal = document.getElementById('createTimesheetModal');

    // Check if the modal exists on the page
    if (createModal) {
        // Listen for when the modal is about to be shown
        createModal.addEventListener('show.bs.modal', function () {
            // Get references to the start and end date input fields
            const startInput = document.getElementById('start_date');
            const endInput = document.getElementById('end_date');

            // Read the data-default attributes set in the HTML
            const defaultStart = startInput.dataset.default;
            const defaultEnd = endInput.dataset.default;

            // If the input is empty, populate it with the default value
            if (startInput && !startInput.value) {
                startInput.value = defaultStart;
            }
            if (endInput && !endInput.value) {
                endInput.value = defaultEnd;
            }
        });
    }
});
