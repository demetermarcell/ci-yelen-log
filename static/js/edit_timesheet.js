document.addEventListener("DOMContentLoaded", function () {
    const MAX_TASKS = 10;

    document.querySelectorAll(".add-task-btn").forEach(function (addBtn) {
        const dayId = addBtn.dataset.dayId;
        const container = document.getElementById(`task-container-${dayId}`);
        const statusSelect = document.querySelector(`select[name="status_${dayId}"]`);

        if (!container || !statusSelect) return;

        // Handle add task button click
        addBtn.addEventListener("click", function () {
            const currentTasks = container.querySelectorAll(".task-row").length;
            if (currentTasks >= MAX_TASKS) {
                alert("You can only add up to 10 tasks per day.");
                return;
            }

            const taskIndex = currentTasks + 1;
            const taskRow = createTaskRow(dayId, taskIndex);
            container.appendChild(taskRow);
        });

        // Handle day status change
        statusSelect.addEventListener("change", function () {
            const selectedStatus = this.value;
            const isWorking = selectedStatus === "working";

            // Show or hide Add Task button
            addBtn.style.display = isWorking ? "inline-block" : "none";

            // Clear tasks if not working
            if (!isWorking) {
                container.innerHTML = "";
            }
        });

        // Initial trigger to apply state
        statusSelect.dispatchEvent(new Event("change"));
    });

    // Handle submit and draft button clicks to set action value
    const submitBtn = document.querySelector("#submitModal .btn-primary");
    const draftBtn = document.querySelector("#draftModal .btn-success");

    if (submitBtn) {
        submitBtn.addEventListener("click", function () {
            document.getElementById("form-action").value = "submit";
        });
    }

    if (draftBtn) {
        draftBtn.addEventListener("click", function () {
            document.getElementById("form-action").value = "draft";
        });
    }
});

/**
 * Create a new task row with predefined task types
 */
function createTaskRow(dayId, index) {
    const row = document.createElement("div");
    row.classList.add("task-row", "mb-3");

    const select = document.createElement("select");
    select.name = `task_type_${dayId}_${index}`;
    select.classList.add("form-select", "mb-2");
    select.required = true;

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select Task";
    select.appendChild(defaultOption);
    // Hardcoded task options as I could not import them from the model properly.
    const taskOptions = [
        ["development", "Development"],
        ["code_review", "Code Review"],
        ["bug_fixing", "Bug Fixing"],
        ["testing", "Testing"],
        ["internal_meeting", "Internal Meeting"],
        ["external_meeting", "External Meeting"],
        ["admin", "Admin"],
        ["documentation", "Documentation"],
        ["support", "Support"],
        ["other", "Other"]
    ];

    taskOptions.forEach(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        select.appendChild(option);
    });

    const input = document.createElement("input");
    input.type = "number";
    input.name = `hours_${dayId}_${index}`;
    input.step = "0.1";
    input.min = "0";
    input.max = "24";
    input.placeholder = "Hours";
    input.classList.add("form-control", "mb-2");
    input.required = true;

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.classList.add("btn", "btn-danger", "btn-sm", "mb-2");
    removeBtn.innerHTML = "&times;";
    removeBtn.title = "Remove Task";
    removeBtn.addEventListener("click", () => {
        row.remove();
    });

    row.appendChild(select);
    row.appendChild(input);
    row.appendChild(removeBtn);

    return row;
}
