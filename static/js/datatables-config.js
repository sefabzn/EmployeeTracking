$(document).ready(function() {
    $('#employeeTable').DataTable({
        "serverSide": true,
        "ajax": "/api/employees/datatable/",
        "columns": [
            {"data": "first_name"},
            {"data": "last_name"},
            {"data": "email"},
            {"data": "remaining_leave_days"},
            {
                "data": "id",
                "render": function(data, type, row) {
                    return `<button onclick="viewDetails(${data})" class="btn btn-sm btn-info">View</button>`;
                }
            }
        ]
    });
});
