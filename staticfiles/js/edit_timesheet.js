document.addEventListener("DOMContentLoaded", function () {
    const MAX_TASKS = 10;

    document.querySelectorAll(".add-task-btn").forEach(function (addBtn) {
        const dayId = addBtn.dataset.dayId;
        const container = document.getElementById(`task-container-${dayId}`);

        if (!container) return;

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
    });
});

/**
 * Create a new task row with hardcoded task type options
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
